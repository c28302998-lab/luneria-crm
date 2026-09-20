import re

with open("frontend/src/app/dashboard/sources/page.tsx", "r") as f:
    content = f.read()

old_button = """                <button 
                  type="submit"
                  className="px-4 py-2 bg-primary border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary/90"
                >
                  Сохранить
                </button>"""

new_button = """                <button type="submit" disabled={isSubmitting} className="px-4 py-2 bg-primary border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary/90 disabled:opacity-50 flex items-center">
                  {isSubmitting ? (
                    <><span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span> Создание...</>
                  ) : "Сохранить"}
                </button>"""

content = content.replace(old_button, new_button)

with open("frontend/src/app/dashboard/sources/page.tsx", "w") as f:
    f.write(content)
