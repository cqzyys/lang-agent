export function isString(value: any): value is string | String {
  return typeof value === "string" || value instanceof String;
}
