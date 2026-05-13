export type FieldType =
  | "string"
  | "text"
  | "date"
  | "number"
  | "enum"
  | "relation"
  | "json_string_array";

export type FieldDefinition = {
  name: string;
  label: string;
  data_type: FieldType;
  required: boolean;
  readonly?: boolean;
  enum_options?: string[];
  relation_target?: string;
  relation_multiple?: boolean;
  placeholder?: string;
};

export type FormSchema = {
  class_name: string;
  title: string;
  fields: FieldDefinition[];
};

export type AgentAction =
  | { name: "show_create_object_form"; payload: { class_name: string; preset_values?: Record<string, unknown> } }
  | { name: "show_object_table"; payload: { class_name: string; rows: Record<string, unknown>[] } }
  | { name: "show_result_notice"; payload: { title: string; message: string; status: "success" | "error" } };

export type AgentResponse = {
  reply: string;
  actions: AgentAction[];
};
