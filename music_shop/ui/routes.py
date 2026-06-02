from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
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


@ui.route("/")
def home():
    filters = {
        "q": request.args.get("q", "").strip(),
        "category": request.args.get("category", "all"),
        "stock": request.args.get("stock", "all"),
    }
    return render_template(
        "home.html",
        categories=repo.list_categories(),
        featured=repo.list_products(featured_only=True, limit=3),
        products=repo.list_products(search=filters["q"], category_slug=filters["category"], stock=filters["stock"]),
        filters=filters,
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

    if request.method == "POST":
        user = authenticate_user(
            request.form["email"].strip().lower(),
            request.form["password"],
        )

        if user:
            login_user(user)

            flash("Вы вошли в систему.", "success")

            return redirect(
                url_for("ui.admin_dashboard")
                if user.is_admin
                else url_for("ui.home")
            )

        flash("Неверная электронная почта или пароль.", "error")

    return render_template("login.html")


@ui.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].strip().lower()

        if repo.get_user_by_email(email):
            flash(
                "Пользователь с такой электронной почтой уже существует.",
                "error",
            )
            return render_template("signup.html")

        try:
            user = repo.create_user(
                email=email,
                name=request.form["name"].strip(),
                password_hash=hash_password(request.form["password"]),
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

            flash(
                "Не удалось создать учетную запись.",
                "error",
            )

    return render_template("signup.html")


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
    if request.method == "POST":
        try:
            order = place_order(
                request.form["name"].strip(),
                request.form["email"].strip().lower(),
                request.form["address"].strip(),
                items,
            )
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("ui.cart"))
        flash("Заказ успешно оформлен.", "success")
        return redirect(url_for("ui.confirmation", order_number=order.order_number))
    return render_template("checkout.html", items=items, totals=totals)


@ui.route("/confirmation/<order_number>")
def confirmation(order_number):
    order = repo.get_order_by_number(order_number)
    if not order:
        return redirect(url_for("ui.home"))
    return render_template("confirmation.html", order=order)


@ui.route("/account")
def account():
    user = current_user()
    if not user or user.is_admin:
        flash("Войдите как покупатель, чтобы посмотреть историю заказов.", "error")
        return redirect(url_for("ui.login"))
    orders = repo.list_orders_for_email(user.email)
    return render_template("account.html", orders=orders)


@ui.route("/admin")
@admin_required
def admin_dashboard():
    categories = repo.list_categories()
    products = repo.list_products()
    orders = repo.list_orders()
    users = repo.list_users()
    return render_template(
        "admin/dashboard.html",
        categories=categories,
        products=products,
        orders=orders,
        revenue=repo.total_revenue(),
        users=users,
        role_labels=ROLE_LABELS,
    )


@ui.route("/admin/products/new", methods=["GET", "POST"])
@ui.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_product_form(product_id=None):
    product = repo.get_product(product_id) if product_id else None
    if request.method == "POST":
        try:
            repo.save_product(product, **product_payload_from_form(request.form, request.files, product))
            flash("Товар обновлен." if product else "Товар создан.", "success")
            return redirect(url_for("ui.admin_dashboard"))
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
    return redirect(url_for("ui.admin_dashboard"))


@ui.post("/admin/categories")
@admin_required
def admin_add_category():
    try:
        name = request.form["name"].strip()
        repo.create_category(
            slug=slugify(name),
            name=name,
            description=request.form.get("description") or "Пользовательская категория.",
            image_url=request.form.get("image_url") or DEFAULT_IMAGE,
        )
        flash("Категория добавлена.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Адрес категории должен быть уникальным.", "error")
    return redirect(url_for("ui.admin_dashboard"))


@ui.post("/admin/categories/<int:category_id>/delete")
@admin_required
def admin_delete_category(category_id):
    try:
        repo.delete_category(category_id)
        flash("Категория удалена.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Нельзя удалить категорию, пока в ней есть товары.", "error")
    return redirect(url_for("ui.admin_dashboard"))


@ui.post("/admin/users")
@admin_required
def admin_create_user():
    try:
        role = request.form["role"] if request.form["role"] in ROLE_LABELS else "viewer"
        repo.create_user(
            email=request.form["email"].strip().lower(),
            name=request.form["name"].strip(),
            password_hash=hash_password(request.form["password"]),
            role=role,
        )
        flash("Учетная запись создана.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Пользователь с такой электронной почтой уже существует.", "error")
    return redirect(url_for("ui.admin_dashboard"))


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
    return redirect(url_for("ui.admin_dashboard"))
