import os
import json
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

# CRITICAL: Import your database model layer.
from my_admin.models import HaircareProducts, SkincareProducts


# =====================================================================
# 1. STRUCTURAL BASE LAYER VIEWS
# =====================================================================

def index_view(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = None

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('admin-dashboard')
            else:
                return redirect('select-category')
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password'})

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not email or not password:
            messages.error(request, "Email and password fields are required.")
            return render(request, 'register.html')

        try:
            if User.objects.filter(username=email).exists():
                messages.error(request, "An account with this email already exists.")
                return render(request, 'register.html')

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.save()

            print(f"✅ Success! User saved in SQLite: {email}")
            return redirect('select-category')

        except IntegrityError as e:
            print(f"❌ Database integrity error: {e}")
            messages.error(request, "A database entry mismatch occurred.")
            return render(request, 'register.html')

    return render(request, 'register.html')


def select_category_view(request):
    return render(request, 'select-category.html')


def skincare_dashboard_view(request):
    return render(request, 'skincare-dashboard.html')


def haircare_dashboard_view(request):
    return render(request, 'haircare-dashboard.html')


def admin_main_dashboard(request):
    """
    Pure Django Dashboard Engine:
    Handles post file streaming, manual addition pipelines, native updates,
    and groups BOTH Skincare and Haircare collections into the admin matrix layout.
    """
    if request.method == 'POST':

        # Helper logic to dynamically clean and convert dirty string input to proper Python Booleans
        def clean_boolean(val):
            if not val:
                return False
            normalized = str(val).strip().lower()
            return normalized in ['true', 'yes', '1', 't', 'y']

        # 1. FORMULATION UPDATE PIPELINE (When product_id is sent from form)
        if request.POST.get('product_id') and request.POST.get('product_id').strip() != "":
            product_id = request.POST.get('product_id')
            category_pipeline = request.POST.get('category_pipeline', 'haircare')

            try:
                if category_pipeline == 'skincare':
                    product = SkincareProducts.objects.get(id=product_id)
                    product.name = request.POST.get('name', product.name)
                    product.category = request.POST.get('category', product.category)
                    product.suitable = clean_boolean(request.POST.get('suitable', str(product.suitable)))
                    product.skin_type = request.POST.get('hair_pattern', product.skin_type)
                    product.primary_concern = request.POST.get('hair_type', product.primary_concern)
                    product.secondary_concern = request.POST.get('scalp_condition', product.secondary_concern)
                    product.product_link = request.POST.get('product_link', product.product_link)
                    product.save()
                else:
                    product = HaircareProducts.objects.get(id=product_id)
                    product.name = request.POST.get('name', product.name)
                    product.category = request.POST.get('category', product.category)
                    product.suitable = clean_boolean(request.POST.get('suitable', str(product.suitable)))
                    product.hair_type = request.POST.get('hair_pattern', product.hair_type)
                    product.hair_pattern = request.POST.get('hair_type', product.hair_pattern)
                    product.scalp_condition = request.POST.get('scalp_condition', product.scalp_condition)
                    product.product_link = request.POST.get('product_link', product.product_link)
                    product.save()

                messages.success(request, f"Changes saved cleanly for product: {product.name}")
            except (HaircareProducts.DoesNotExist, SkincareProducts.DoesNotExist):
                messages.error(request, "Target specification record not found.")
            except Exception as e:
                messages.error(request, f"Execution Error: {e}")

        # 2. MANUAL NEW PRODUCT INGESTION PIPELINE (When product_id is missing/blank)
        elif request.POST.get('name') and not request.FILES.get('csv_file'):
            category_pipeline = request.POST.get('category_pipeline', 'haircare')
            try:
                if category_pipeline == 'skincare':
                    new_product = SkincareProducts.objects.create(
                        name=request.POST.get('name'),
                        category=request.POST.get('category', 'Cleanser'),
                        suitable=clean_boolean(request.POST.get('suitable', 'True')),
                        skin_type=request.POST.get('hair_pattern', 'Normal'),
                        primary_concern=request.POST.get('hair_type', 'Normal'),
                        secondary_concern=request.POST.get('scalp_condition', 'Normal'),
                        product_link=request.POST.get('product_link', '')
                    )
                else:
                    new_product = HaircareProducts.objects.create(
                        name=request.POST.get('name'),
                        category=request.POST.get('category', 'Shampoo'),
                        suitable=clean_boolean(request.POST.get('suitable', 'True')),
                        hair_type=request.POST.get('hair_pattern', 'Straight'),
                        hair_pattern=request.POST.get('hair_type', 'Normal'),
                        scalp_condition=request.POST.get('scalp_condition', 'Normal'),
                        product_link=request.POST.get('product_link', '')
                    )
                messages.success(request, f"Successfully created new formulation: {new_product.name}")
            except Exception as e:
                messages.error(request, f"Manual Ingestion Failure: {e}")

        # 3. CSV BATCH PIPELINE UPLOAD
        elif request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            try:
                df = pd.read_csv(csv_file).fillna("")
                df.columns = df.columns.str.strip().str.lower()

                is_skin_csv = 'skin' in csv_file.name.lower()

                for _, row in df.iterrows():
                    if is_skin_csv:
                        SkincareProducts.objects.create(
                            name=row.get('name', 'Unknown Skin SKU'),
                            category=row.get('category', 'Cleanser'),
                            suitable=clean_boolean(row.get('suitable', 'True')),
                            skin_type=row.get('skin_type', 'Normal'),
                            primary_concern=row.get('primary_concern', 'Normal'),
                            secondary_concern=row.get('secondary_concern', 'Normal'),
                            product_link=row.get('product_link', '')
                        )
                    else:
                        HaircareProducts.objects.create(
                            name=row.get('name', 'Unknown Hair Matrix SKU'),
                            category=row.get('category', 'Shampoo'),
                            suitable=clean_boolean(row.get('suitable', 'True')),
                            hair_type=row.get('hair_type', 'Normal'),
                            hair_pattern=row.get('hair_pattern', 'Straight'),
                            scalp_condition=row.get('scalp_condition', 'Normal'),
                            product_link=row.get('product_link', '')
                        )
                messages.success(request, "Integrated uploaded file records into database matrix.")
            except Exception as e:
                messages.error(request, f"CSV Processing Failure: {e}")

    # Fetch live elements from BOTH database models
    db_hair = HaircareProducts.objects.all()
    db_skin = SkincareProducts.objects.all()

    # Calculate 48-hour time benchmark boundary
    time_threshold = timezone.now() - timedelta(hours=48)
    formatted_list = []

    # Map Skincare entries to tracking dictionary format
    for prod in db_skin:
        is_new_asset = False
        if hasattr(prod, 'created_at') and prod.created_at:
            is_new_asset = prod.created_at >= time_threshold
        elif request.method == 'POST' and request.POST.get('name') and prod.name == request.POST.get('name'):
            is_new_asset = True

        formatted_list.append({
            'id': prod.id,
            'cat': 'skincare',
            'name': prod.name,
            'typeMatch': prod.skin_type,
            'primaryConcern': prod.primary_concern,
            'secondaryConcern': prod.secondary_concern,
            'productType': prod.category,
            'productLink': prod.product_link if prod.product_link else '',
            'suitable': str(prod.suitable),
            'description': '',
            'is_new': is_new_asset
        })

    # Map Haircare entries to tracking dictionary format
    for prod in db_hair:
        is_new_asset = False
        if hasattr(prod, 'created_at') and prod.created_at:
            is_new_asset = prod.created_at >= time_threshold
        elif request.method == 'POST' and request.POST.get('name') and prod.name == request.POST.get('name'):
            is_new_asset = True

        formatted_list.append({
            'id': prod.id,
            'cat': 'haircare',
            'name': prod.name,
            'typeMatch': prod.hair_type,
            'primaryConcern': prod.hair_pattern,
            'secondaryConcern': prod.scalp_condition,
            'productType': prod.category,
            'productLink': prod.product_link if prod.product_link else '',
            'suitable': str(prod.suitable),
            'description': '',
            'is_new': is_new_asset
        })

    # Sort array dynamically so newest additions load first
    formatted_list.sort(key=lambda x: x['id'], reverse=True)

    json_data_stream = json.dumps(formatted_list)
    return render(request, 'admin-dashboard.html', {'pandas_catalog': json_data_stream})


# =====================================================================
# 2. DATA DECK LAYOUTS
# =====================================================================

def haircare_products_views(request):
    user_pattern = request.GET.get('pattern', '').strip().lower()
    user_thickness = request.GET.get('thickness', '').strip().lower()
    user_scalp = request.GET.get('scalp', '').strip().lower()

    filtered_db_query = HaircareProducts.objects.all()

    if user_pattern:
        filtered_db_query = filtered_db_query.filter(hair_type__iexact=user_pattern)

    if user_thickness:
        filtered_db_query = filtered_db_query.filter(hair_pattern__iexact=user_thickness)

    if user_scalp:
        if user_scalp in ["balanced", "normal"]:
            filtered_db_query = filtered_db_query.filter(
                scalp_condition__icontains="balanced") | filtered_db_query.filter(scalp_condition__icontains="normal")
        elif user_scalp in ["flaky", "dry"]:
            filtered_db_query = filtered_db_query.filter(scalp_condition__icontains="flaky") | filtered_db_query.filter(
                scalp_condition__icontains="dry")
        else:
            filtered_db_query = filtered_db_query.filter(scalp_condition__icontains=user_scalp)

    grouped_products = {
        'Shampoo': [],
        'Conditioner': [],
        'Serum': [],
        'Hair Mask': []
    }

    for product in filtered_db_query:
        cat_name = str(product.category).strip().title() if product.category else "Shampoo"

        if cat_name in grouped_products:
            grouped_products[cat_name].append(product)
        else:
            if "Shampoo" in cat_name:
                grouped_products['Shampoo'].append(product)
            elif "Conditioner" in cat_name:
                grouped_products['Conditioner'].append(product)
            elif "Serum" in cat_name or "Treatment" in cat_name:
                grouped_products['Serum'].append(product)
            elif "Mask" in cat_name:
                grouped_products['Hair Mask'].append(product)

    context = {
        'grouped_products': grouped_products,
        'pattern': user_pattern,
        'thickness': user_thickness,
        'scalp': user_scalp,
    }

    return render(request, 'haircare-products.html', context)


def skincare_recommendation_view(request):
    """
    Assembles a personalized multi-step skincare timeline using partial-match
    filtering to ensure products surface cleanly matching user choices.
    """
    user_skin_type = request.GET.get('skin_type', '').strip().lower()
    user_primary = request.GET.get('primary_concern', '').strip().lower()
    user_secondary = request.GET.get('secondary_concern', '').strip().lower()

    # Start with all active database products
    filtered_db_query = SkincareProducts.objects.all()

    # 1. Flexible Skin Type Matching (Handles variations or multi-type matches)
    if user_skin_type:
        filtered_db_query = filtered_db_query.filter(skin_type__icontains=user_skin_type)

    # 2. Flexible Concern Matching (Uses OR condition logic to map broad concerns)
    if user_primary or user_secondary:
        from django.db.models import Q
        concern_queries = Q()

        if user_primary:
            concern_queries |= Q(primary_concern__icontains=user_primary) | Q(secondary_concern__icontains=user_primary)
        if user_secondary:
            concern_queries |= Q(primary_concern__icontains=user_secondary) | Q(
                secondary_concern__icontains=user_secondary)

        filtered_db_query = filtered_db_query.filter(concern_queries)

    # 3. Setup sequential timeline grouping arrays
    grouped_products = {
        'Cleanse / Purify': [],
        'Treat (Targeted Serums)': [],
        'Hydrate / Nourish': [],
        'Protect (SPF Base)': []
    }

    # 4. Sort into their matching step columns
    for product in filtered_db_query:
        cat_name = str(product.category).strip().title() if product.category else "Cleanser"

        if any(keyword in cat_name for keyword in ["Cleanse", "Wash", "Cleanser"]):
            grouped_products['Cleanse / Purify'].append(product)
        elif any(keyword in cat_name for keyword in ["Serum", "Treat", "Ampoule"]):
            grouped_products['Treat (Targeted Serums)'].append(product)
        elif any(keyword in cat_name for keyword in ["Moisturizer", "Cream", "Hydrate", "Gel"]):
            grouped_products['Hydrate / Nourish'].append(product)
        elif any(keyword in cat_name for keyword in ["Sunscreen", "Spf", "Protect"]):
            grouped_products['Protect (SPF Base)'].append(product)

    context = {
        'grouped_products': grouped_products,
        'skin_type': user_skin_type,
        'primary': user_primary,
        'secondary': user_secondary,
    }

    return render(request, 'skincare-products.html', context)