import frappe
from frappe import _
from frappe.utils import cint


def _normalize_avatar(avatar):
	if avatar and "http:" not in avatar and "https:" not in avatar and not avatar.startswith("/"):
		return "/" + avatar
	return avatar or ""


@frappe.whitelist(allow_guest=True)
def get_posts(category=None, blogger=None, start=0, page_length=12):
	"""Published blog posts for slife_app's own /blog listing page.

	Delegates to blog app's own get_blog_list (same cover-image fallback,
	author join and comment counts it uses for its native listing), instead
	of re-deriving that query here, so results stay consistent with blog
	app's own behaviour.
	"""
	if not frappe.db.exists("DocType", "Blog Post"):
		return []

	from blog.blog.doctype.blog_post.blog_post import get_blog_list

	filters = {}
	if category:
		filters["blog_category"] = category
	if blogger:
		filters["blogger"] = blogger

	posts = get_blog_list(
		"Blog Post",
		filters=filters,
		limit_start=cint(start),
		limit_page_length=cint(page_length),
	)

	return [
		{
			"title": post.title,
			"route": post.route,
			"intro": post.intro,
			"published_on": post.published,
			"read_time": post.read_time,
			"featured": bool(post.featured),
			"cover_image": post.cover_image,
			"category": post.category,
			"author": {
				"name": post.blogger,
				"full_name": post.full_name,
				"avatar": _normalize_avatar(post.avatar),
			},
			"comment_text": post.comment_text,
		}
		for post in posts
	]


@frappe.whitelist(allow_guest=True)
def get_post(route):
	"""A single published blog post by its route, for a post detail page."""
	if not frappe.db.exists("DocType", "Blog Post"):
		frappe.throw(_("Blog post not found"), frappe.DoesNotExistError)

	from frappe.utils import global_date_format
	from frappe.website.utils import find_first_image, get_html_content_based_on_type

	name = frappe.db.get_value("Blog Post", {"route": route, "published": 1}, "name")
	if not name:
		frappe.throw(_("Blog post not found"), frappe.DoesNotExistError)

	post = frappe.get_doc("Blog Post", name)
	content = get_html_content_based_on_type(post, "content", post.content_type)
	blogger = frappe.get_doc("Blogger", post.blogger)
	category = frappe.db.get_value(
		"Blog Category", post.blog_category, ["name", "route", "title"], as_dict=True
	)

	return {
		"title": post.title,
		"route": post.route,
		"published_on": global_date_format(post.published_on),
		"read_time": post.read_time,
		"content": content,
		"cover_image": post.meta_image or find_first_image(content),
		"category": category,
		"author": {
			"name": blogger.name,
			"full_name": blogger.full_name,
			"avatar": _normalize_avatar(blogger.avatar),
			"bio": blogger.bio,
		},
	}
