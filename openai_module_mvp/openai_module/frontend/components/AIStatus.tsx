import React from "react";

export default function AIStatus({ provider="openai" }: {provider?: string}){
  return (
    <div className="text-xs opacity-70">AI Provider: <b>{provider}</b></div>
  );
}
