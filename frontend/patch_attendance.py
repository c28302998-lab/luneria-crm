with open("src/app/dashboard/attendance/page.tsx", "r") as f:
    content = f.read()

# Add candidates state
content = content.replace("const [attendance, setAttendance] = useState<any[]>([]);", "const [attendance, setAttendance] = useState<any[]>([]);\n  const [candidates, setCandidates] = useState<Record<number, string>>({});")

# Fetch candidates in fetchData
new_fetch = """      const [{ data: wData }, { data: aData }, { data: cData }] = await Promise.all([
        api.get('/workers/'),
        api.get('/attendance/', { params: { target_date: targetDate } }),
        api.get('/candidates/')
      ]);
      
      const cMap: Record<number, string> = {};
      cData.forEach((c: any) => {
        cMap[c.id] = c.first_name || `Кандидат #${c.id}`;
      });
      setCandidates(cMap);
"""
content = content.replace("const [{ data: wData }, { data: aData }] = await Promise.all([\n        api.get('/workers/'),\n        api.get('/attendance/', { params: { target_date: targetDate } })\n      ]);", new_fetch)

# Update display
old_display = "Работник #{worker.id} (Кандидат #{worker.candidate_id})"
new_display = "{candidates[worker.candidate_id] || `Работник #${worker.id}`}"
content = content.replace(old_display, new_display)

with open("src/app/dashboard/attendance/page.tsx", "w") as f:
    f.write(content)
