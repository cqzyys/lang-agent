import { Node } from "@xyflow/react";

export const genStateList = (nodes: Node[]) => {
  let states: string[] = [];
  let schema = {};

  //构建messages的状态变量
  nodes.forEach((node) => {
    const type = node.type;
    const name: string = node.data["name"] as string;

    if (type === "start") {
      const state_schema = node.data["state_schema"] as string;

      if (typeof state_schema === "string") {
        schema = JSON.parse(state_schema);
      }
    }
    states.push("messages['" + name + "']");
  });

  //构建非messages的状态变量
  Object.keys(schema).forEach((key) => {
    if (key !== "messages") {
      states.push(key);
    }
  });

  return states;
};
