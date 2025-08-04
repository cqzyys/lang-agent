import { addToast, Input } from "@heroui/react";
import { memo } from "react";

import { Icon } from "@/components";

function KeyInput({ id }: Record<string, string>) {
  return (
    <Input
      isReadOnly
      endContent={
        <Icon
          color="white"
          size={18}
          type="copy"
          onClick={() => {
            navigator.clipboard.writeText(id).then(() => {
              addToast({
                title: "已复制到剪贴板",
                color: "success",
                timeout: 800,
              });
            });
          }}
        />
      }
      label="Key"
      name="key"
      radius="sm"
      size="sm"
      value={id}
    />
  );
}

export default memo(KeyInput);
