
export interface FnData{
    name: string,
    code: string
    isCustom: boolean
}

export interface MinMaxArgParam{
  name: string,
  min: number,
  max: number,
  step: number
}

export interface ValueArgParam{
  name: string
  value: number,
}

export type ParamTypes = MinMaxArgParam | ValueArgParam

export interface AlgorithmData {
  name: string,
  args: (ParamTypes)[] 
  isUsed?: boolean
}

export interface AlhoritmParamSchema{
  type: string,
  name: string
}

export interface AlgorithmSchema {
  name: string,
  args: AlhoritmParamSchema[] 
  isUsed?: boolean
}