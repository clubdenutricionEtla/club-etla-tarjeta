with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_fn = '''def upload_product_image(file_storage):
    if not file_storage or not SUPABASE_SERVICE_KEY:
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else 'jpg'
    filename = f"{secrets.token_hex(8)}.{ext}"
    file_bytes = file_storage.read()
    upload_url = f"{SUPABASE_URL}/storage/v1/object/product-images/{filename}"
    resp = http_requests.post(
        upload_url,
        headers={
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': file_storage.mimetype or 'image/jpeg'
        },
        data=file_bytes
    )
    if resp.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"
    return None'''

new_fn = '''def upload_product_image(file_storage):
    if not file_storage:
        print("⚠️ DEBUG upload: no llegó ningún archivo")
        return None
    if not SUPABASE_SERVICE_KEY:
        print("⚠️ DEBUG upload: SUPABASE_SERVICE_KEY no está configurada")
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else 'jpg'
    filename = f"{secrets.token_hex(8)}.{ext}"
    file_bytes = file_storage.read()
    print(f"🔍 DEBUG upload: subiendo {filename}, {len(file_bytes)} bytes")
    upload_url = f"{SUPABASE_URL}/storage/v1/object/product-images/{filename}"
    resp = http_requests.post(
        upload_url,
        headers={
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': file_storage.mimetype or 'image/jpeg'
        },
        data=file_bytes
    )
    print(f"🔍 DEBUG upload: respuesta {resp.status_code} - {resp.text[:300]}")
    if resp.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"
    return None'''

n = content.count(old_fn)
if n == 1:
    content = content.replace(old_fn, new_fn, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Diagnóstico agregado a upload_product_image")
else:
    print(f"⚠️ No coincide (encontrado {n} veces)")
