import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def submit_contact_form(name=None, email=None, message=None, services=None):
    """Store a submission from the website's /contact form.

    Guest-facing, so every field is untrusted input - validated here rather
    than left to the DocType alone, since a missing/blank value should be a
    clean 400 rather than a raw DB constraint error.
    """
    name = (name or "").strip()
    email = (email or "").strip()
    message = (message or "").strip()

    if not name or not email or not message:
        frappe.throw(_("Name, email and message are required"), frappe.ValidationError)

    if not frappe.utils.validate_email_address(email, throw=False):
        frappe.throw(_("Please enter a valid email address"), frappe.ValidationError)

    if isinstance(services, str):
        services = frappe.parse_json(services) if services.strip().startswith("[") else [services]
    services_text = ", ".join(s for s in (services or []) if s)

    doc = frappe.get_doc(
        {
            "doctype": "Contact Submission",
            "contact_name": name,
            "email": email,
            "message": message,
            "services": services_text,
            # a logged-in (non-Guest) session is staff/dev poking at the form,
            # not a real customer - keep it out of genuine submission data
            "is_test": 1 if frappe.session.user != "Guest" else 0,
        }
    )
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"name": doc.name}
