"use client";

import { useEffect, useState } from "react";

import { searchRelationOptions } from "@/lib/api";

type Props = {
  className: string;
  value: number | "";
  onChange: (value: number | "") => void;
};

export function RelationSelect({ className, value, onChange }: Props) {
  const [keyword, setKeyword] = useState("");
  const [options, setOptions] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    const handle = setTimeout(async () => {
      const data = await searchRelationOptions(className, keyword);
      setOptions(data.items);
    }, 250);
    return () => clearTimeout(handle);
  }, [className, keyword]);

  return (
    <div className="field-stack">
      <input
        className="input"
        value={keyword}
        placeholder={`搜索${className}`}
        onChange={(event) => setKeyword(event.target.value)}
      />
      <select
        className="input"
        value={value}
        onChange={(event) => onChange(event.target.value ? Number(event.target.value) : "")}
      >
        <option value="">请选择</option>
        {options.map((option) => {
          const display = (option.name ?? option.title ?? option.id) as string | number;
          return (
            <option key={String(option.id)} value={String(option.id)}>
              {display}
            </option>
          );
        })}
      </select>
    </div>
  );
}
