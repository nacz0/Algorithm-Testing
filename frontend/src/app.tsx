
import { useState, useEffect } from "preact/hooks"

import AlgorytmsSection from "./components/AlogrytmsSection/AlogrytmsSection.tsx"
import CustomFnSection from "./components/CustomFnSection/FnSection.tsx"
import Raport from "./components/Raport/Raport.tsx"
import './app.css'
import funcionsData from "./data/functions.json"
import algorithms_config from "./data/algorithms.json"
import { SharedParamsSection } from "./components/SharedParamsSection/SharedParamsSection.tsx"
import type { AlgorithmData, AlhoritmParamSchema, ParamTypes, FnData, AlgorithmSchema } from "./interfaces.ts"



const convertAlgsParams = (algorithms: AlgorithmSchema[]): AlgorithmData[] =>{
    let result: AlgorithmData[] = algorithms.map(data =>{

      if (window.localStorage.getItem("algParams-" + data.name)){
        return JSON.parse(window.localStorage.getItem("algParams-" + data.name) as string)
      }

      return ({
        name: data.name,
        args: data.args.map(param => {
            if (param.type == "min-max"){
              return {name: param.name, min: 1, max: 5, step: 0.1}
            }else{
              return {name: param.name, value: 5}
            }
        }),
        isUsed: true
      })
    })

    return result
}

const convertSharedAlgsParams = (sharedParams:AlhoritmParamSchema[]): (ParamTypes)[] => {

  return sharedParams.map(param => {
    if (param.type ==  "min-max"){
      return {name: param.name, min: 1, max: 5, step: 0.1}
    }else{
      return {name: param.name, value: 5}
    }
  })
}

export function App() {
  const [selectedFnData, setSelectedFnData] = useState<FnData>({name: funcionsData[0].name, code: funcionsData[0].code, isCustom: false})
  const [algorithmsData, setAlgorithmsData] = useState<AlgorithmData[]>(convertAlgsParams(algorithms_config.algorithms))
  const [sharedAlgsParams, setSharedAlgsParams] = useState<(ParamTypes)[]>(convertSharedAlgsParams(algorithms_config.shared_args))

  //TODO: Przywróć proces zapisu i odczytu argumentów
  useEffect(() => {
    for (let algorithmData of algorithmsData) {
    window.localStorage.setItem("algParams-" + algorithmData.name, JSON.stringify(algorithmData))
    }
  }, [algorithmsData])

  return (
    <div>
      <h1>Testowanie algorytmów heurystycznych</h1>
      <CustomFnSection setFn={setSelectedFnData} selectedFn={selectedFnData}  fnsData={funcionsData}/>
      <SharedParamsSection sharedAlgsParams={sharedAlgsParams} setSharedAlgsParams={setSharedAlgsParams}/>
      <AlgorytmsSection algorithmData={algorithmsData} setAlgorithmData={setAlgorithmsData}/>
      <Raport selectedFnData={selectedFnData} algorithmsData={algorithmsData} sharedAlgsParams={sharedAlgsParams} />
    </div>
  )
}
