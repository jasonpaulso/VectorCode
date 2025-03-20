local utils = require("vectorcode.utils")
---@class VectorCode.JobRunner
---@field run_async fun(args: string[], callback:fun(result: table, error: table)?, bufnr: integer):(job_handle:integer?)
---@field run fun(args: string[], timeout_ms: integer?, bufnr: integer):(result:table, error:table)
---@field is_job_running fun(job_handle: integer):boolean
---@field stop_job fun(job_handle: integer)

return {
  --- Automatically find project_root from buffer path if it's not already specified.
  ---@param args string[]
  ---@param bufnr integer
  ---@return string[]
  find_root = function(args, bufnr)
    if not vim.list_contains(args, "--project_root") then
      local find_root = utils.find_root(bufnr)
      if find_root then
        vim.list_extend(args, { "--project_root", find_root })
      end
    end
    return args
  end,
}
