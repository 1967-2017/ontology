"use client";

import { FormEvent, useEffect, useState } from "react";

import { createObject, fetchFormSchema } from "@/lib/api";
import { FieldDefinition, FormSchema } from "@/types/ontology";
import { RelationSelect } from "./RelationSelect";

const EMPTY_PRESET_VALUES: Record<string, unknown> = {};

type Props = {
  className: string;
  presetValues?: Record<string, unknown>;
  themeColor?: string;
  onNotice?: (notice: { title: string; message: string; status: "success" | "error" }) => void;
};

export function CreateOntologyObjectCard({ className, presetValues, themeColor, onNotice }: Props) {
  const stablePresetValues = presetValues ?? EMPTY_PRESET_VALUES;
  const presetValuesKey = JSON.stringify(stablePresetValues);
  const [schema, setSchema] = useState<FormSchema | null>(null);
  const [values, setValues] = useState<Record<string, unknown>>(stablePresetValues);
  const [submitting, setSubmitting] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoadError(null);
    fetchFormSchema(className)
      .then((result) => {
        if (!active) {
          return;
        }
        setSchema(result);
        setValues(buildInitialValues(result, stablePresetValues));
      })
      .catch((error) => {
        if (!active) {
          return;
        }
        setSchema(null);
        setLoadError(error instanceof Error ? error.message : "表单加载失败");
      });
    return () => {
      active = false;
    };
  }, [className, presetValuesKey]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!schema) {
      return;
    }

    const missingField = schema.fields.find((field) => {
      if (!field.required) {
        return false;
      }
      const currentValue = values[field.name];
      if (field.data_type === "json_string_array") {
        return !Array.isArray(currentValue) || currentValue.length === 0;
      }
      return currentValue === undefined || currentValue === null || currentValue === "";
    });

    if (missingField) {
      onNotice?.({
        title: "表单校验失败",
        message: `${missingField.label}为必填项，请先填写或选择。`,
        status: "error",
      });
      return;
    }

    setSubmitting(true);
    try {
      const result = await createObject(className, values);
      if (result.graph_sync.status === "failed") {
        onNotice?.({
          title: "创建成功，但图同步失败",
          message: result.graph_sync.message ?? "Neo4j 同步失败",
          status: "error",
        });
      } else {
        onNotice?.({
          title: "创建成功",
          message: `${className} 已创建并同步到图数据库`,
          status: "success",
        });
      }
      if (schema) {
        setValues(buildInitialValues(schema, stablePresetValues));
      }
    } catch (error) {
      onNotice?.({
        title: "创建失败",
        message: error instanceof Error ? error.message : "未知错误",
        status: "error",
      });
    } finally {
      setSubmitting(false);
    }
  }

  function updateField(field: FieldDefinition, value: unknown) {
    setValues((current) => ({ ...current, [field.name]: value }));
  }

  return (
    <section className="card" style={{ borderTopColor: themeColor ?? "var(--accent)" }}>
      <div className="card-header">
        <div>
          <p className="eyebrow">{className}</p>
          <h3>{schema?.title ?? "加载表单中"}</h3>
        </div>
      </div>
      {loadError ? <p className="error-text">表单加载失败：{loadError}</p> : null}
      <form className="form-grid" onSubmit={handleSubmit}>
        {schema?.fields.map((field) => (
          <label className="field-stack" key={field.name}>
            <span>
              {field.label}
              {field.required ? " *" : ""}
            </span>
            <FieldRenderer field={field} value={values[field.name]} onChange={(value) => updateField(field, value)} />
          </label>
        ))}
        <button className="button" disabled={submitting || !schema} type="submit">
          {submitting ? "提交中..." : "提交创建"}
        </button>
      </form>
    </section>
  );
}

type RendererProps = {
  field: FieldDefinition;
  value: unknown;
  onChange: (value: unknown) => void;
};

function FieldRenderer({ field, value, onChange }: RendererProps) {
  if (field.data_type === "text") {
    return <textarea className="input textarea" value={(value as string) ?? ""} onChange={(e) => onChange(e.target.value)} />;
  }
  if (field.data_type === "number") {
    return <input className="input" type="number" value={(value as string | number) ?? ""} onChange={(e) => onChange(e.target.value ? Number(e.target.value) : "")} />;
  }
  if (field.data_type === "date") {
    return <input className="input" type="date" value={(value as string) ?? ""} onChange={(e) => onChange(e.target.value || null)} />;
  }
  if (field.data_type === "enum") {
    return (
      <select className="input" value={(value as string) ?? ""} onChange={(e) => onChange(e.target.value)}>
        <option value="">请选择</option>
        {field.enum_options?.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  }
  if (field.data_type === "relation" && field.relation_target) {
    return <RelationSelect className={field.relation_target} value={(value as number) ?? ""} onChange={onChange as (value: number | "") => void} />;
  }
  if (field.data_type === "json_string_array") {
    return (
      <input
        className="input"
        value={Array.isArray(value) ? value.join(",") : ""}
        placeholder="React, FastAPI, Neo4j"
        onChange={(e) => onChange(e.target.value.split(",").map((item) => item.trim()).filter(Boolean))}
      />
    );
  }
  return (
    <input
      className="input"
      type="text"
      value={(value as string) ?? ""}
      placeholder={field.placeholder ?? ""}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

function buildInitialValues(schema: FormSchema, presetValues: Record<string, unknown>) {
  const initialValues = schema.fields.reduce<Record<string, unknown>>((acc, field) => {
    if (field.data_type === "json_string_array") {
      acc[field.name] = [];
    }
    return acc;
  }, {});

  return { ...initialValues, ...normalizePresetValues(schema, presetValues) };
}

function normalizePresetValues(schema: FormSchema, presetValues: Record<string, unknown>) {
  const allowedFieldNames = new Set(schema.fields.map((field) => field.name));
  const normalized: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(presetValues)) {
    const normalizedKey = mapPresetAlias(schema.class_name, key);
    if (allowedFieldNames.has(normalizedKey)) {
      normalized[normalizedKey] = value;
    }
  }

  return normalized;
}

function mapPresetAlias(className: string, key: string) {
  if (className === "Task") {
    if (key === "developer_id" || key === "assignee_id") {
      return "assignee_developer_id";
    }
    if (key === "project" || key === "projectId") {
      return "project_id";
    }
  }

  if (className === "Team" && (key === "leader_id" || key === "developer_id")) {
    return "leader_developer_id";
  }

  if (className === "Developer" && key === "teamId") {
    return "team_id";
  }

  return key;
}
