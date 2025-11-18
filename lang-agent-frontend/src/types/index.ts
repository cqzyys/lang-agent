import { SVGProps } from "react";
export * from "@/types/edges";
export * from "@/types/api";

export type IconProps = SVGProps<SVGSVGElement> & {
  size?: number;
  type: string;
  onClick?: React.MouseEventHandler<SVGSVGElement>;
};
