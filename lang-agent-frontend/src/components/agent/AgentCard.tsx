import { memo } from "react";
import { addToast, Card, CardBody, CardHeader, Switch } from "@heroui/react";
import { useNavigate } from "react-router-dom";

import { apiClient } from "@/util";
import { Agent } from "@/types";
import { Icon } from "@/components";

export type AgentCardData = {
  agent: Agent;
  onDelete: () => void;
};

function AgentCard({ agent, onDelete }: AgentCardData) {
  const navigate = useNavigate();

  function onValueChange(value: boolean) {
    apiClient
      .post("/v1/agent/update", { ...agent, reuse_flag: value })
      .then(() => {
        addToast({
          title: "修改成功",
          timeout: 1000,
          shouldShowTimeoutProgress: true,
        });
      })
      .catch((error) => {
        addToast({
          title: "修改失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      });
  }

  function handleDelete() {
    apiClient
      .post(`/v1/agent/delete?id=${agent.id}`)
      .then(() => {
        onDelete();
        addToast({
          title: "删除成功",
          timeout: 1000,
          shouldShowTimeoutProgress: true,
        });
      })
      .catch((error) => {
        addToast({
          title: "删除失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      });
  }

  return (
    <Card isPressable className="w-[300px] h-[150px]" radius="md">
      <CardHeader className="">
        <div className="flex justify-between items-center w-full">
          <div className="font-semibold text-sm">{agent.name}</div>
          <div className="ml-auto mr-4">
            <Switch
              defaultSelected={agent.reuse_flag}
              size="sm"
              onValueChange={onValueChange}
            >
              复用
            </Switch>
          </div>
          <div>
            <Icon size={18} type="trash" onClick={handleDelete} />
          </div>
        </div>
      </CardHeader>
      <CardBody
        onClick={() => {
          navigate("/flow", { state: { init_agent: agent } });
        }}
      >
        <div className="font-serif font-medium text-sm">
          {agent.description}
        </div>
      </CardBody>
    </Card>
  );
}

export default memo(AgentCard);
