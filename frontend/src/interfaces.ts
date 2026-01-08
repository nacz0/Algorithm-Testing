
export interface FnData {
    name: string;
    code: string;
    bounds: [number, number];
    isCustom: boolean;
}


export interface MinMaxArgParam{
  name: string,
  min: number,
  max: number,
  type: "int" | "float"
}

export interface ValueArgParam{
  name: string
  value: number,
  type: "int" | "float"
}

export type ParamTypes = MinMaxArgParam | ValueArgParam

export interface AlgorithmData {
  name: string,
  params: (ParamTypes)[] 
  isUsed?: boolean
}

export interface AlhoritmParamSchema{
  type: string,
  name: string
}

export interface AlgorithmSchema {
  name: string,
  params: AlhoritmParamSchema[] 
  isUsed?: boolean
}