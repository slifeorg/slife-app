import frappe


def free_blog_route(*args, **kwargs):
	"""Keep /blog pointed at slife_app's own www/blog.html.

	The `blog` app ships its Blog Post DocType with a DocType-level
	`route` of "blog" (its built-in listing-page route, not the
	per-document route used for /blog/<category>/<post>). Frappe turns
	any has_web_view DocType with a route into an implicit website route
	rule (frappe.website.path_resolver.get_website_rules), so "/blog"
	gets hijacked into that generic listing before slife_app's own page
	is ever considered. That lookup reads tabDocType.route directly via
	frappe.get_all, bypassing Property Setters, so a Customize Form
	override has no effect here - the DocType row itself must be cleared.
	blog app's fixture sync (on every bench migrate) restores route="blog"
	from its JSON, so this has to re-run on every migrate, not just once.
	"""
	if not frappe.db.exists("DocType", "Blog Post"):
		return

	if frappe.db.get_value("DocType", "Blog Post", "route") == "blog":
		frappe.db.set_value("DocType", "Blog Post", "route", "", update_modified=False)
		frappe.clear_cache()


def restore_blog_route(*args, **kwargs):
	"""Undo free_blog_route() when slife_app is removed.

	Without slife_app's www/blog.html around to claim it, /blog should go
	back to blog app's own DocType-level route so its native Blog Post
	listing works again, matching what a fresh blog-app-only install
	would have.
	"""
	if not frappe.db.exists("DocType", "Blog Post"):
		return

	if frappe.db.get_value("DocType", "Blog Post", "route") == "":
		frappe.db.set_value("DocType", "Blog Post", "route", "blog", update_modified=False)
		frappe.clear_cache()
