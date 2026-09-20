import re

with open("frontend/src/app/dashboard/reports/page.tsx", "r") as f:
    content = f.read()

old_td = '<td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-y-2 flex flex-col items-end">'
new_td = '<td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">\n                    <div className="flex flex-col items-end space-y-2">'

content = content.replace(old_td, new_td)

old_end_td = """                  </td>
                </tr>"""
new_end_td = """                    </div>
                  </td>
                </tr>"""
content = content.replace(old_end_td, new_end_td)

# Let's ensure proof_url starts with http
def fix_href(match):
    return '{r.data?.proof_url && (\n                      <a href={r.data.proof_url.startsWith("http") ? r.data.proof_url : "https://" + r.data.proof_url} target="_blank"'

content = re.sub(r'\{r\.data\?\.proof_url && \(\s*<a href=\{r\.data\.proof_url\} target="_blank"', fix_href, content)

with open("frontend/src/app/dashboard/reports/page.tsx", "w") as f:
    f.write(content)
