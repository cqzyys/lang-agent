import { addToast } from "@heroui/react";
import { useEffect, useState } from "react";

import { apiClient } from "@/util";
import { Agent } from "@/types";
import { AgentCard, InitCard } from "@/components";

export default function AgentPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const fetchData = async () => {
    apiClient
      .get("/v1/agent/list")
      .then((response) => {
        setAgents(response.data.data);
      })
      .catch((error) => {
        addToast({
          title: "获取Agent数据失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="flex flex-wrap">
      {agents.map((agent) => {
        return (
          <div key={agent.id} className="m-4 mt-0">
            <AgentCard
              agent={agent}
              onDelete={() => {
                fetchData();
              }}
            />
          </div>
        );
      })}
      <div className="m-4 mt-0">
        <InitCard />
      </div>
    </div>
  );
}
