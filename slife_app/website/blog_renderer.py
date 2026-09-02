import frappe
from frappe.website.page_renderers.base_renderer import BaseRenderer


class BlogPageRenderer(BaseRenderer):
	"""Serve slife_app's own SvelteKit shell for every /blog... request.

	blog app's native renderers - ListPage for /blog/<category>, DocumentPage
	for /blog/<category>/<title> - build their Jinja context by calling
	frappe.get_doc() on the category/post and frappe.throw() on anything
	stale or unpublished (e.g. "Blog Category erpnext-woocommerce not found"),
	and gate on doc-level permissions that differ for guests vs logged-in
	users. Registered via the page_renderer hook, this runs before
	DocumentPage/TemplatePage/ListPage (frappe.website.path_resolver), so
	none of that native logic executes - slife_app always serves blog.html,
	and the SvelteKit app resolves the actual post/category client-side via
	slife_app.api.blog.get_post / get_posts instead.

	frappe.local.path (set in frappe.website.path_resolver.resolve_path,
	before any website_route_rules rewrite the endpoint) is used rather than
	self.path, since by the time renderers run, blog app's own
	"/blog/<category>" rule has already rewritten the endpoint to the
	literal string "Blog Post" for two-segment paths.
	"""

	def can_render(self):
		path = getattr(frappe.local, "path", None) or self.path
		path = path.strip("/ ")
		return path == "blog" or path.startswith("blog/")

	def render(self):
		path = (getattr(frappe.local, "path", None) or self.path).strip("/ ")
		# bare /blog -> the SvelteKit listing shell; anything deeper -> a
		# plain hand-written page that fetches the post via slife_app.api.blog
		filename = "blog.html" if path == "blog" else "blog_post.html"
		with open(frappe.get_app_path("slife_app", "www", filename), "rb") as f:
			html = f.read().decode("utf-8")
		return self.build_response(html)
