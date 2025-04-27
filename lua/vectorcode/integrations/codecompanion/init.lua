---@module "codecompanion"

---@class VectorCode.CodeCompanion.ToolOpts
---@field max_num integer?
---@field default_num integer?
---@field include_stderr boolean?
---@field use_lsp boolean?
---@field auto_submit table<string, boolean>?
---@field ls_on_start boolean?
---@field no_duplicate boolean?

local vc_config = require("vectorcode.config")
local check_cli_wrap = vc_config.check_cli_wrap
local notify_opts = vc_config.notify_opts
local logger = vc_config.logger

local tool_result_source = "VectorCodeToolResult"

---@param t table|string
---@return string
local function flatten_table_to_string(t)
  if type(t) == "string" then
    return t
  end
  return table.concat(vim.iter(t):flatten(math.huge):totable(), "\n")
end

local job_runner = nil
---@param use_lsp boolean
local function initialise_runner(use_lsp)
  if job_runner == nil then
    if use_lsp then
      job_runner = require("vectorcode.jobrunner.lsp")
    end
    if job_runner == nil then
      job_runner = require("vectorcode.jobrunner.cmd")
      logger.info("Using cmd runner for CodeCompanion tool.")
      if use_lsp then
        vim.schedule_wrap(vim.notify)(
          "Failed to initialise the LSP runner. Falling back to cmd runner.",
          vim.log.levels.WARN,
          notify_opts
        )
      end
    else
      logger.info("Using LSP runner for CodeCompanion tool.")
    end
  end
end

return {
  chat = {
    ---@param component_cb (fun(result:VectorCode.Result):string)?
    make_slash_command = check_cli_wrap(function(component_cb)
      return {
        description = "Add relevant files from the codebase.",
        ---@param chat CodeCompanion.Chat
        callback = function(chat)
          local codebase_prompt = ""
          local vc_cache = vc_config.get_cacher_backend()
          local bufnr = chat.context.bufnr
          if not vc_cache.buf_is_registered(bufnr) then
            return
          end
          codebase_prompt =
            "The following are relevant files from the repository. Use them as extra context."
          local query_result = vc_cache.make_prompt_component(bufnr, component_cb)
          local id = tostring(query_result.count) .. " file(s) from codebase"
          codebase_prompt = codebase_prompt .. query_result.content
          chat:add_message(
            { content = codebase_prompt, role = "user" },
            { visible = false, id = id }
          )
          chat.references:add({
            source = "VectorCode",
            name = "VectorCode",
            id = id,
          })
        end,
      }
    end),

    make_tool = function(opts)
      local has = require("codecompanion").has
      if has == nil or has("xml-tools") then
        return require("vectorcode.integrations.codecompanion.legacy_tool")(opts)
      elseif has("function-calling") then
        return require("vectorcode.integrations.codecompanion.func_calling_tool")(opts)
      else
        error("Unsupported version of codecompanion!")
      end
    end,
  },
}
