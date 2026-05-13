from app.schemas.ontology import FormSchema


def build_form_schema(class_name: str, label: str, fields):
    return FormSchema(class_name=class_name, title=f"创建{label}", fields=fields)
