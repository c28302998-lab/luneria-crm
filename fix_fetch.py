with open("frontend/src/app/dashboard/crm-accounts/page.tsx", "r") as f:
    content = f.read()

import re

# We need to extract fetchUsers and move it outside useEffect
old_use_effect = """  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const { data } = await api.get('/users/');
        // Only show WORKERS and ADMINS/CURATORS, basically everyone
        setUsers(data.filter((u: any) => u.role === 'WORKER'));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    if (user?.role === 'OWNER') {
      fetchUsers();
    }
  }, [user]);"""

new_code = """  const fetchUsers = async () => {
    try {
      const { data } = await api.get('/users/');
      setUsers(data.filter((u: any) => u.role === 'WORKER'));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === 'OWNER') {
      fetchUsers();
    }
  }, [user]);"""

if old_use_effect in content:
    content = content.replace(old_use_effect, new_code)
else:
    print("Warning: could not find old useEffect")

with open("frontend/src/app/dashboard/crm-accounts/page.tsx", "w") as f:
    f.write(content)
