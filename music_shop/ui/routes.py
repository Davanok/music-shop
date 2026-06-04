import re

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
from music_shop.data.enums import OrderStatus
from music_shop.data.services import (
    DEFAULT_IMAGE,
    ROLE_LABELS,
    add_to_cart,
    admin_required,
    authenticate_user,
    cart_items,
    cart_totals,
    current_user,
    hash_password,
    login_user,
    logout_user,
    place_order,
    product_gallery,
    product_payload_from_form,
    slugify,
    update_cart,
)

ui = Blueprint("ui", __name__)

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_login_form(form):
    data = {
        "email": form.get("email", "").strip().lower(),
        "password": form.get("password", ""),
    }
    errors = {}

    if not data["email"]:
        errors["email"] = "Введите электронную почту."
    elif not EMAIL_RE.match(data["email"]):
        errors["email"] = "Введите корректный адрес электронной почты."

    if not data["password"]:
        errors["password"] = "Введите пароль."

    return data, errors


def validate_signup_form(form):
    data = {
        "name": form.get("name", "").strip(),
        "email": form.get("email", "").strip().lower(),
        "password": form.get("password", ""),
    }
    errors = {}

    if not data["name"]:
        errors["name"] = "Введите имя."
    elif len(data["name"]) < 2:
        errors["name"] = "Имя должно быть не короче 2 символов."

    if not data["email"]:
        errors["email"] = "Введите электронную почту."
    elif not EMAIL_RE.match(data["email"]):
        errors["email"] = "Введите корректный адрес электронной почты."

    if not data["password"]:
        errors["password"] = "Введите пароль."
    elif len(data["password"]) < 8:
        errors["password"] = "Пароль должен содержать минимум 8 символов."

    return data, errors


def get_filters():
    return {
        "q": request.args.get("q", "").strip(),
        "category": request.args.get("category", "all"),
        "stock": request.args.get("stock", "all"),
    }

@ui.route("/")
def home():
    return render_template(
        "home.html",
        categories=repo.list_categories(),
        featured=repo.list_products(featured_only=True, limit=3),
    )


@ui.route("/login", methods=["GET", "POST"])
def login():
    user = current_user()
    if user:
        return redirect(
            url_for("ui.admin_dashboard")
            if user.is_admin
            else url_for("ui.account")
        )

    form = {"email": ""}
    errors = {}

    if request.method == "POST":
        form, errors = validate_login_form(request.form)

        if not errors:
            user = authenticate_user(
                form["email"],
                form["password"],
            )

            if user:
                login_user(user)

                flash("Вы вошли в систему.", "success")

                return redirect(
                    url_for("ui.admin_dashboard")
                    if user.is_admin
                    else url_for("ui.home")
                )

            errors = {
                "email": "Проверьте адрес электронной почты.",
                "password": "Проверьте пароль.",
            }
            flash("Неверная электронная почта или пароль.", "error")
        else:
            flash("Исправьте ошибки в форме входа.", "error")

    return render_template("login.html", errors=errors, form=form)


@ui.route("/signup", methods=["GET", "POST"])
def signup():
    form = {"name": "", "email": ""}
    errors = {}

    if request.method == "POST":
        form, errors = validate_signup_form(request.form)

        if not errors and repo.get_user_by_email(form["email"]):
            errors["email"] = "Пользователь с такой электронной почтой уже существует."

        if errors:
            flash("Исправьте ошибки в форме регистрации.", "error")
            return render_template("signup.html", errors=errors, form=form)

        try:
            user = repo.create_user(
                email=form["email"],
                name=form["name"],
                password_hash=hash_password(form["password"]),
                role="viewer",
            )

            login_user(user)

            flash(
                "Регистрация завершена. Вы вошли в систему.",
                "success",
            )

            return redirect(url_for("ui.home"))

        except IntegrityError:
            db.session.rollback()
            errors["email"] = "Пользователь с такой электронной почтой уже существует."
            flash("Не удалось создать учетную запись.", "error")

    return render_template("signup.html", errors=errors, form=form)


@ui.post("/logout")
def logout():
    logout_user()
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("ui.home"))


@ui.route("/products/<slug>")
def product_detail(slug):
    product = repo.get_product_by_slug(slug)
    if not product:
        flash("Товар не найден.", "error")
        return redirect(url_for("ui.home"))
    return render_template("product_detail.html", product=product, gallery=product_gallery(product))


@ui.post("/cart/add/<int:product_id>")
def add_cart_item(product_id):
    if add_to_cart(product_id, request.form.get("quantity", 1)):
        flash("Товар добавлен в корзину.", "success")
    else:
        flash("Товар сейчас недоступен.", "error")
    return redirect(request.referrer or url_for("ui.cart"))


@ui.route("/cart", methods=["GET", "POST"])
def cart():
    if request.method == "POST":
        quantities = {
            key.replace("quantity_", ""): int(value or 0)
            for key, value in request.form.items()
            if key.startswith("quantity_")
        }
        update_cart(quantities)
        flash("Корзина обновлена.", "success")
        return redirect(url_for("ui.cart"))
    items = cart_items()
    return render_template("cart.html", items=items, totals=cart_totals(items))


@ui.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = cart_items()
    if not items:
        flash("Ваша корзина пуста.", "error")
        return redirect(url_for("ui.cart"))
    totals = cart_totals(items)
    user = current_user()
    if not user:
        flash("Войдите, чтобы оформить заказ.", "error")
        return redirect(url_for("ui.login"))

    if request.method == "POST":
        try:
            order = place_order(
                user.name,
                user.email,
                {
                    "country": request.form.get("country", ""),
                    "city": request.form.get("city", ""),
                    "street": request.form.get("street", ""),
                    "postal_code": request.form.get("postal_code", ""),
                },
                items,
            )
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("ui.cart"))
        flash("Заказ успешно оформлен.", "success")
        return redirect(url_for("ui.confirmation", order_number=order.order_number))
    return render_template("checkout.html", items=items, totals=totals, user=user)


@ui.route("/confirmation/<order_number>")
def confirmation(order_number):
    order = repo.get_order_by_number(order_number)
    if not order:
        return redirect(url_for("ui.home"))
    return render_template("confirmation.html", order=order)


@ui.route("/account")
def account():
    user = current_user()
    if not user:
        flash("Войдите, чтобы посмотреть историю заказов.", "error")
        return redirect(url_for("ui.login"))
    orders = repo.list_orders_for_email(user.email)
    return render_template("account.html", orders=orders)


@ui.route("/admin")
@admin_required
def admin_dashboard():
    allowed_sections = {"products", "categories", "users", "orders"}
    active_section = request.args.get("section", "products")
    if active_section not in allowed_sections:
        active_section = "products"

    entry_id = request.args.get("entry_id", type=int)
    is_adding = request.args.get("action") == "new"

    categories = repo.list_categories()
    products = repo.list_products()
    orders = repo.list_orders()
    users = repo.list_users()

    selected_product = repo.get_product(entry_id) if active_section == "products" and entry_id else None
    selected_category = repo.get_category(entry_id) if active_section == "categories" and entry_id else None
    selected_user = repo.get_user(entry_id) if active_section == "users" and entry_id else None
    selected_order = repo.get_order(entry_id) if active_section == "orders" and entry_id else None

    return render_template(
        "admin/dashboard.html",
        active_section=active_section,
        categories=categories,
        products=products,
        orders=orders,
        revenue=repo.total_revenue(),
        users=users,
        role_labels=ROLE_LABELS,
        order_statuses=list(OrderStatus),
        is_adding=is_adding,
        selected_product=selected_product,
        selected_category=selected_category,
        selected_user=selected_user,
        selected_order=selected_order,
    )


@ui.route("/admin/products/new", methods=["GET", "POST"])
@ui.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_product_form(product_id=None):
    product = repo.get_product(product_id) if product_id else None
    if request.method == "POST":
        try:
            saved_product = repo.save_product(product, **product_payload_from_form(request.form, request.files, product))
            flash("Товар обновлен." if product else "Товар создан.", "success")
            return redirect(url_for("ui.admin_dashboard", section="products", entry_id=saved_product.id))
        except IntegrityError:
            db.session.rollback()
            flash("Адрес товара должен быть уникальным.", "error")
    return render_template("admin/product_form.html", product=product, categories=repo.list_categories())


@ui.post("/admin/products/<int:product_id>/delete")
@admin_required
def admin_delete_product(product_id):
    try:
        repo.delete_product(product_id)
        flash("Товар удален.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Нельзя удалить товар, который есть в заказе.", "error")
    return redirect(url_for("ui.admin_dashboard", section="products"))


@ui.post("/admin/categories")
@admin_required
def admin_add_category():
    try:
        name = request.form["name"].strip()
        category = repo.create_category(
            slug=slugify(request.form.get("slug") or name),
            name=name,
            description=request.form.get("description") or "Пользовательская категория.",
            image_url=request.form.get("image_url") or DEFAULT_IMAGE,
        )
        flash("Категория добавлена.", "success")
        return redirect(url_for("ui.admin_dashboard", section="categories", entry_id=category.id))
    except IntegrityError:
        db.session.rollback()
        flash("Адрес категории должен быть уникальным.", "error")
    return redirect(url_for("ui.admin_dashboard", section="categories", action="new"))


@ui.post("/admin/categories/<int:category_id>/edit")
@admin_required
def admin_update_category(category_id):
    try:
        name = request.form["name"].strip()
        repo.update_category(
            category_id,
            slug=slugify(request.form.get("slug") or name),
            name=name,
            description=request.form.get("description") or "Пользовательская категория.",
            image_url=request.form.get("image_url") or DEFAULT_IMAGE,
        )
        flash("Категория обновлена.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Адрес категории должен быть уникальным.", "error")
    return redirect(url_for("ui.admin_dashboard", section="categories", entry_id=category_id))


@ui.post("/admin/categories/<int:category_id>/delete")
@admin_required
def admin_delete_category(category_id):
    try:
        repo.delete_category(category_id)
        flash("Категория удалена.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Нельзя удалить категорию, пока в ней есть товары.", "error")
    return redirect(url_for("ui.admin_dashboard", section="categories"))


@ui.post("/admin/users")
@admin_required
def admin_create_user():
    try:
        role = request.form["role"] if request.form["role"] in ROLE_LABELS else "viewer"
        user = repo.create_user(
            email=request.form["email"].strip().lower(),
            name=request.form["name"].strip(),
            password_hash=hash_password(request.form["password"]),
            role=role,
        )
        flash("Учетная запись создана.", "success")
        return redirect(url_for("ui.admin_dashboard", section="users", entry_id=user.id))
    except IntegrityError:
        db.session.rollback()
        flash("Пользователь с такой электронной почтой уже существует.", "error")
    return redirect(url_for("ui.admin_dashboard", section="users", action="new"))


@ui.post("/admin/users/<int:user_id>/edit")
@admin_required
def admin_update_user(user_id):
    try:
        role = request.form["role"] if request.form["role"] in ROLE_LABELS else "viewer"
        if current_user() and user_id == current_user().id and role != "admin":
            role = "admin"
            flash("Нельзя снять роль администратора у своей учетной записи.", "error")
        password = request.form.get("password", "")
        password_hash = hash_password(password) if password else None
        repo.update_user(
            user_id,
            email=request.form["email"].strip().lower(),
            name=request.form["name"].strip(),
            role=role,
            password_hash=password_hash,
        )
        flash("Пользователь обновлен.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Пользователь с такой электронной почтой уже существует.", "error")
    return redirect(url_for("ui.admin_dashboard", section="users", entry_id=user_id))


@ui.post("/admin/users/<int:user_id>/role")
@admin_required
def admin_update_user_role(user_id):
    role = request.form["role"] if request.form["role"] in ROLE_LABELS else "viewer"
    user = repo.update_user_role(user_id, role)
    if user and current_user() and user.id == current_user().id and user.role != "admin":
        user.role = "admin"
        db.session.commit()
        flash("Нельзя снять роль администратора у своей учетной записи.", "error")
    else:
        flash("Роль пользователя обновлена.", "success")
    return redirect(url_for("ui.admin_dashboard", section="users", entry_id=user_id))


@ui.post("/admin/orders/<int:order_id>/status")
@admin_required
def admin_update_order_status(order_id):
    status_value = request.form.get("status")
    try:
        status = OrderStatus(status_value)
    except ValueError:
        flash("Некорректный статус заказа.", "error")
        return redirect(url_for("ui.admin_dashboard", section="orders", entry_id=order_id))

    repo.update_order_status(order_id, status)
    flash("Статус заказа обновлен.", "success")
    return redirect(url_for("ui.admin_dashboard", section="orders", entry_id=order_id))


@ui.route("/catalog")
def catalog():
    filters = get_filters()

    return render_template(
        "catalog.html",
        categories=repo.list_categories(),
        products=repo.list_products(
            search=filters["q"],
            category_slug=filters["category"],
            stock=filters["stock"],
        ),
        filters=filters,
    )


@ui.route("/catalog/products")
def catalog_products():
    filters = get_filters()

    return render_template(
        "partials/product_grid.html",
        products=repo.list_products(
            search=filters["q"],
            category_slug=filters["category"],
            stock=filters["stock"],
        ),
    )
