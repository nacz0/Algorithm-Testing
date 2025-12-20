import type { ParamTypes } from "../../interfaces"

interface Props{
    sharedAlgsParams: (ParamTypes)[],
    setSharedAlgsParams: React.Dispatch<React.SetStateAction<(ParamTypes)[]>>
}

export function SharedParamsSection({sharedAlgsParams, setSharedAlgsParams}: Props) {

    const changeParam = (paramIndex:number, type: "min"|"max"|"step"|"value", value:string ) =>{
       // @ts-ignore
        setSharedAlgsParams((params) => {
       
            const sharedAlgsParamsCopy = JSON.parse(JSON.stringify(params))
             sharedAlgsParamsCopy[paramIndex][type] = Number(value)
             return sharedAlgsParamsCopy
        })
    }

  return (
  <>
    <h2>Wpólne parametry:</h2>
    <div className="algorithm-card">            
        <div className="param-labels">
            <div className="label-space"></div>
            <div className="label-text">Min</div>
            <div className="separator"></div>
            <div className="label-text">Max</div>
            <div className="separator"></div>
            <div className="label-text">Step</div>
        </div>
        
        {sharedAlgsParams.map((arg, index) =>  {
            if ("value" in arg){
                return <div className="param-row">
                    <label>{arg.name}:</label> 
                    <input onChange={(e) =>changeParam(index, "value", e.currentTarget.value )} value={arg.value} type="number" min={0}/>
                </div>
            }

            if ("step" in arg){
                return  <div className="param-row">
                            <label>{arg.name}:</label>
                            <input onChange={(e) =>changeParam(index, "min", e.currentTarget.value )} value={arg.min} type="number" step={1} min={0}/>
                            <span className="separator">-</span>
                            <input onChange={(e) =>changeParam(index, "max", e.currentTarget.value )}  value={arg.max} type="number" step={1} min={0}/>
                            <span className="separator">,</span>
                            <input onChange={(e) =>changeParam(index, "step", e.currentTarget.value )} value={arg.step} type="number" step={1} min={0}/>
                        </div>
            }

        })}        
    </div>
        </>
  )
}
