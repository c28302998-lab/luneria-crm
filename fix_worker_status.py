import re

with open("frontend/src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

# Add handleStatusChange
handler = """
  const handleStatusChange = async (newStatus: string) => {
    try {
      await api.patch(`/workers/${id}/status?status=${newStatus}`);
      setWorker({...worker, status: newStatus});
    } catch (err) {
      alert('Ошибка при изменении статуса');
    }
  };
"""
content = content.replace("  const fetchData = async () => {", handler + "\n  const fetchData = async () => {")

# Replace status span with select
old_status = """                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${
                  worker.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {worker.status}
                </span>"""

new_status = """                {user?.role === 'ADMIN' || user?.role === 'OWNER' ? (
                  <select 
                    value={worker.status}
                    onChange={(e) => handleStatusChange(e.target.value)}
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold mt-1 border-0 cursor-pointer focus:ring-0 ${
                      worker.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 
                      worker.status === 'TERMINATED' ? 'bg-red-100 text-red-800' : 
                      'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <option value="ACTIVE" className="bg-white text-black">ACTIVE</option>
                    <option value="PAUSED" className="bg-white text-black">PAUSED</option>
                    <option value="TERMINATED" className="bg-white text-black">TERMINATED</option>
                  </select>
                ) : (
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold mt-1 ${
                    worker.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 
                    worker.status === 'TERMINATED' ? 'bg-red-100 text-red-800' : 
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {worker.status}
                  </span>
                )}"""

content = content.replace(old_status, new_status)

with open("frontend/src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
