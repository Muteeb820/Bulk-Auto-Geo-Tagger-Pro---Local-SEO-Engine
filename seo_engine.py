import os
import piexif
from PIL import Image
from datetime import datetime

# --- GPS Math Conversion ---
def to_deg(value, loc):
    if value < 0: loc_value = loc[0]
    elif value > 0: loc_value = loc[1]
    else: loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return (deg, min, sec, loc_value)

def change_to_rational(number):
    f = 100000
    return (int(number * f), f)

# --- Parse details.txt ---
def read_details_file(file_path):
    data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, val = line.split('=', 1)
                    data[key.strip().lower()] = val.strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return data

# --- The Deep EXIF Injector ---
def inject_exif_data(img_path, data, keep_original=False):
    try:
        img = Image.open(img_path)
        
        orig_format = img.format if img.format else 'JPEG'
        if orig_format == 'MPO': orig_format = 'JPEG'
            
        # 🛠️ Extract or Create Blank EXIF
        raw_exif = img.info.get("exif")
        if raw_exif:
            try:
                exif_dict = piexif.load(raw_exif)
            except:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
        else:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}

        # ==========================================
        # 1. AUTO-GENERATED PREMIUM PROPERTIES
        # ==========================================
        exif_dict['0th'][18246] = 5  # 5-Star Rating
        exif_dict['0th'][18249] = 99 # Rating Percent
        
        current_time = datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')
        exif_dict['0th'][piexif.ImageIFD.DateTime] = current_time
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = current_time
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = current_time
        
        exif_dict['0th'][piexif.ImageIFD.Software] = b"Adobe Photoshop Lightroom Classic 12.0"
        exif_dict['0th'][piexif.ImageIFD.HostComputer] = b"Windows 11 Pro"
        exif_dict['0th'][piexif.ImageIFD.ImageWidth] = img.width
        exif_dict['0th'][piexif.ImageIFD.ImageLength] = img.height

        # ==========================================
        # 2. CUSTOM DATA INJECTION FROM details.txt
        # ==========================================
        if 'lat' in data and 'long' in data:
            lat = float(data['lat'])
            lng = float(data['long'])
            lat_deg = to_deg(lat, ["S", "N"])
            lng_deg = to_deg(lng, ["W", "E"])
            
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = lat_deg[3]
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = [change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2])]
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = lng_deg[3]
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = [change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2])]

        if 'make' in data: exif_dict['0th'][piexif.ImageIFD.Make] = data['make'].encode('utf-8')
        if 'model' in data: exif_dict['0th'][piexif.ImageIFD.Model] = data['model'].encode('utf-8')
        if 'copyright' in data: exif_dict['0th'][piexif.ImageIFD.Copyright] = data['copyright'].encode('utf-8')
        if 'author' in data: 
            exif_dict['0th'][piexif.ImageIFD.Artist] = data['author'].encode('utf-8')
            exif_dict['0th'][piexif.ImageIFD.XPAuthor] = data['author'].encode('utf-16le')
        if 'title' in data: 
            exif_dict['0th'][piexif.ImageIFD.ImageDescription] = data['title'].encode('utf-8')
            exif_dict['0th'][piexif.ImageIFD.XPTitle] = data['title'].encode('utf-16le')
        if 'keywords' in data: 
            exif_dict['0th'][piexif.ImageIFD.XPKeywords] = data['keywords'].encode('utf-16le')
        if 'headline' in data:
            exif_dict['0th'][piexif.ImageIFD.XPSubject] = data['headline'].encode('utf-16le')

        full_comment = f"{data.get('desc', '')} | City: {data.get('city', '')}, {data.get('province', '')}, {data.get('country', '')} | Website: {data.get('website', '')} | Credit: {data.get('credit', '')}"
        exif_dict['0th'][piexif.ImageIFD.XPComment] = full_comment.encode('utf-16le')
        exif_dict['Exif'][piexif.ExifIFD.UserComment] = b"UNICODE\x00" + full_comment.encode('utf-16le')

        # --- SAVE IMAGE LOGIC ---
        exif_bytes = piexif.dump(exif_dict)
        save_kwargs = {'exif': exif_bytes}
        
        if keep_original:
            if orig_format in ['JPEG', 'JPG']:
                save_kwargs['quality'] = 100
            img.save(img_path, orig_format, **save_kwargs)
            return orig_format
        else:
            save_kwargs['quality'] = 100
            img.save(img_path, "JPEG", **save_kwargs)
            return "JPEG"

    except Exception as e:
        print(f"❌ Failed to tag {os.path.basename(img_path)}: {str(e)}")
        return None

# --- Master Crawler ---
def process_master_folder(master_folder, mode):
    print("\n🚀 Initiating Enterprise SEO Media Engine...\n")
    
    for location_dir in os.listdir(master_folder):
        loc_path = os.path.join(master_folder, location_dir)
        
        if os.path.isdir(loc_path):
            details_file = os.path.join(loc_path, 'details.txt')
            
            if os.path.exists(details_file):
                print(f"📂 Processing Location Folder: {location_dir}")
                seo_data = read_details_file(details_file)
                
                for root, dirs, files in os.walk(loc_path):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            img_path = os.path.join(root, file)
                            
                            # MODE 1: CONVERT TO JPG
                            if mode == '1':
                                if not file.lower().endswith(('.jpg', '.jpeg')):
                                    new_jpg_path = os.path.splitext(img_path)[0] + ".jpg"
                                    try:
                                        print(f"  🔄 Converting {file} -> JPG")
                                        img = Image.open(img_path)
                                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                                        img.save(new_jpg_path, "JPEG", quality=100)
                                        os.remove(img_path)
                                        img_path = new_jpg_path
                                    except Exception as e:
                                        continue
                                
                                fmt = inject_exif_data(img_path, seo_data, keep_original=False)
                                if fmt: print(f"  ✅ Tagged (JPG): {os.path.basename(img_path)}")
                            
                            # MODE 2: KEEP ORIGINAL FORMAT
                            elif mode == '2':
                                fmt = inject_exif_data(img_path, seo_data, keep_original=True)
                                if fmt: print(f"  ✅ Tagged ({fmt}): {os.path.basename(img_path)}")
                                
                print("-" * 50)
            else:
                pass

# --- INTERACTIVE MENU ---
def main_menu():
    print("=" * 70)
    print("         🌟 ULTIMATE LOCAL SEO IMAGE ENGINE 🌟")
    print("=" * 70)
    print("\nPlease choose your processing mode:\n")
    
    print("[1] CONVERT ALL TO JPG (Recommended for Full SEO & Windows)")
    print("    -> Converts WebP and PNG to JPG automatically.")
    print("    -> 100% EXIF data WILL BE VISIBLE in Windows Properties.")
    print("    -> Best for Google Business Profiles and Local SEO.\n")
    
    print("[2] KEEP ORIGINAL FORMATS (WebP / PNG / JPG)")
    print("    -> Leaves WebP and PNG exactly in their original format.")
    print("    -> EXIF data is injected deeply for Google Bots, BUT...")
    print("    -> Data WILL NOT SHOW in Windows Properties for WebP/PNG.\n")
    
    choice = input("Enter 1 or 2 (and press Enter): ").strip()
    
    if choice not in ['1', '2']:
        print("\n❌ Invalid choice. Please run the script again and type 1 or 2.")
        return
        
    current_directory = os.path.dirname(os.path.abspath(__file__))
    process_master_folder(current_directory, choice)

if __name__ == "__main__":
    main_menu()