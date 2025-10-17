import { memo } from "react";
import { Card, CardBody, CardHeader } from "@heroui/react";
import { useNavigate } from "react-router-dom";

import { Icon } from "@/components";
const App: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Card
      isPressable
      className="w-[300px] h-[150px]"
      radius="md"
      onPress={() => {
        navigate("/flow", { state: { init_agent: undefined } });
      }}
    >
      <CardHeader className="">
        <div className="flex justify-between w-full">
          <div className="font-semibold text-sm">新增Agent</div>
        </div>
      </CardHeader>
      <CardBody>
        <div className="font-serif font-medium text-sm flex items-center justify-center h-full">
          <Icon size={30} type="add" />
        </div>
      </CardBody>
    </Card>
  );
};

export default memo(App);
