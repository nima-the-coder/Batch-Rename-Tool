import os
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog


class BatchRenamer:
    def __init__(self):
        self.files_renamed = 0
        self.errors = []

    def get_folder_path(self):
        """گرفتن مسیر پوشه از کاربر"""

        class FolderSelector:
            def __init__(self):
                self.root = tk.Tk()
                self.root.title("select folder")
                self.root.geometry("400x300")

            def get_folder_path(self):
                """با استفاده از dialog پوشه انتخاب میکند"""
                self.root.withdraw()

                user_folder_path = filedialog.askdirectory(
                    title="پوشه مورد نظر را انتخاب کنید",
                    initialdir=os.path.expanduser("~")  # شروع از پوشه کاربر
                )

                self.root.destroy()

                if user_folder_path and os.path.exists(user_folder_path):
                    return user_folder_path
                else:
                    return None

        # استفاده:
        selector = FolderSelector()
        path = selector.get_folder_path()
        print(f"مسیر انتخاب شده: {path}")
        return path

    def list_files(self, user_folder_path):

        # 1. بررسی وجود پوشه
        if not os.path.exists(user_folder_path):
            print(f"❌ پوشه '{user_folder_path}' وجود ندارد!")
            self.errors.append(f"پوشه وجود ندارد: {user_folder_path}")
            return []

        if not os.path.isdir(user_folder_path):
            print(f"❌ '{user_folder_path}' یک پوشه نیست!")
            self.errors.append(f"مسیر پوشه نیست: {user_folder_path}")
            return []

        try:
            # 2. گرفتن همه آیتم‌های پوشه
            all_items = os.listdir(user_folder_path)
            files_only = []  # 👈 این متغیر نهایی هست

            # 3. فقط فایل‌ها (نه پوشه‌ها)
            for item in all_items:
                item_path = os.path.join(user_folder_path, item)

                # بررسی اینکه آیا فایل هست
                if os.path.isfile(item_path):
                    files_only.append(item)

            # 4. نمایش نتیجه (همه فایل‌ها)
            print(f"📁 در پوشه '{os.path.basename(user_folder_path)}' پیدا شد:")
            print(f"📄 تعداد کل فایل‌ها: {len(files_only)}")

            # نمایش همه فایل‌ها
            if files_only:
                print("🧾 لیست کامل فایل‌ها:")
                for num, file in enumerate(files_only, 1):
                    print(f"file number{num:3}: {file}")  # :3 برای تراز کردن شماره
            else:
                print("⚠️  هیچ فایلی در این پوشه نیست.")

            return files_only  # 👈 این رو برمی‌گردونه

        except PermissionError:
            print(f"❌ دسترسی به پوشه '{user_folder_path}' مجاز نیست!")
            self.errors.append(f"خطای دسترسی: {user_folder_path}")
            return []
        except Exception as e:
            print(f"❌ خطای ناشناخته: {e}")
            self.errors.append(f"خطای عمومی: {e}")
            return []

    @staticmethod
    def get_prefix_from_user(default="file"):
        """فقط یک بار پیشوند رو می‌گیره"""
        root = tk.Tk()
        root.withdraw()

        user_prefix = tk.simpledialog.askstring(
            "پیشوند",
            "پیشوند برای همه فایل‌ها را وارد کنید:",
            initialvalue=default
        )

        root.destroy()
        return user_prefix if user_prefix else default

    @staticmethod
    def generate_new_name(old_name, new_prefix, index, padding=3):
        """حالا با پیشوند آماده"""
        name_without_ext, file_extension = os.path.splitext(old_name)
        number_str = str(index).zfill(padding)
        new_name = f"{new_prefix}_{number_str}{file_extension}"
        return new_name

    def execute_rename(self, user_folder_path, files_changes_list, new_prefix):
        """
        اجرای تغییر نام با لیست تغییرات آماده
        files_changes_list: لیست (نام قدیمی, نام جدید)
        """
        confirm = input(f"\n❓ تغییر نام {len(files_changes_list)} فایل؟ (y/n): ").strip().lower()

        if confirm != 'y':
            print("❌ لغو شد")
            return

        print(f"\n⚙️  در حال تغییر نام...")
        success_count = 0

        for old_name, new_name in files_changes_list:  # حالا از لیست می‌خونیم
            try:
                old_path = os.path.join(user_folder_path, old_name)
                new_path = os.path.join(user_folder_path, new_name)

                os.rename(old_path, new_path)
                print(f"✅ {old_name} → {new_name}")
                success_count += 1
                self.files_renamed += 1

            except Exception as e:
                print(f"❌ خطا در {old_name}: {e}")
                self.errors.append(f"{old_name}: {e}")

        # گزارش
        self.save_report(user_folder_path, new_prefix, files_changes_list, success_count)

        print(f"\n📊 نتیجه: {success_count}/{len(files_changes_list)} موفق")

    @staticmethod
    def save_report(user_folder_path, user_prefix, files_changes_list, success_count):
        """ذخیره گزارش با لیست تغییرات"""
        from datetime import datetime

        try:
            report_path = os.path.join(user_folder_path, f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"تاریخ: {datetime.now()}\n")
                f.write(f"پوشه: {user_folder_path}\n")
                f.write(f"پیشوند: {user_prefix}\n")
                f.write(f"موفق: {success_count}/{len(files_changes_list)}\n\n")

                for i, (old_name, new_name) in enumerate(files_changes_list, 1):
                    f.write(f"{i}. {old_name} → {new_name}\n")

            print(f"📄 گزارش: {report_path}")

        except Exception as e:
            print(f"⚠️ خطا در گزارش: {e}")


if __name__ == "__main__":
    renamer = BatchRenamer()

    folder_path = renamer.get_folder_path()

    if folder_path:
        all_files = renamer.list_files(folder_path)

        if all_files:
            prefix = renamer.get_prefix_from_user()

            # 1. ساخت لیست تغییرات
            changes_list = []  # لیست جدید

            print(f"\n📝 پیش‌نمایش (پیشوند: '{prefix}'):")
            for listNum, old_file_name in enumerate(all_files, start=1):
                new_file_name = renamer.generate_new_name(old_file_name, prefix, listNum)
                changes_list.append((old_file_name, new_file_name))  # ذخیره در لیست
                print(f"{listNum}. {old_file_name} → {new_file_name}")

            # 2. حالا می‌تونیم از changes_list استفاده کنیم
            print(f"\n✅ لیست تغییرات ساخته شد: {len(changes_list)} آیتم")

            # 3. به تابع execute_rename بده
            renamer.execute_rename(folder_path, changes_list, prefix)