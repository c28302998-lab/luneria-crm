with open("frontend/src/app/dashboard/emails/page.tsx", "r") as f:
    content = f.read()

# Add state variables
state_vars = """  const [workers, setWorkers] = useState<any[]>([]);
  const [admins, setAdmins] = useState<any[]>([]);
  const [showHistoryModal, setShowHistoryModal] = useState<number | null>(null);
  const [accountHistory, setAccountHistory] = useState<any[]>([]);"""

content = content.replace("  const [workers, setWorkers] = useState<any[]>([]);\n  const [admins, setAdmins] = useState<any[]>([]);", state_vars)

# Add fetch history function if not exists
fetch_func = """  const fetchHistory = async (accId: number) => {
    try {
      // If endpoint doesn't exist yet, we just set empty
      // const { data } = await api.get(`/emails/accounts/${accId}/history`);
      // setAccountHistory(data);
      setAccountHistory([]);
      setShowHistoryModal(accId);
    } catch (e) {
      console.error(e);
      alert("История недоступна");
    }
  };
"""
if "fetchHistory" not in content:
    content = content.replace("  const fetchWorkers", fetch_func + "\n  const fetchWorkers")

with open("frontend/src/app/dashboard/emails/page.tsx", "w") as f:
    f.write(content)
