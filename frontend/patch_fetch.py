with open("src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

import re

old_fetch = """  const fetchData = async () => {
    try {
      setLoading(true);
      const { data: wData } = await api.get(`/workers/${id}`);
      setWorker(wData.worker);
      setCandidate(wData.candidate);
      setUserAccount(wData.user_account);
      setReports(wData.reports);
      setAdmin(wData.admin);
      setAccountInfo(wData.worker.account_info || '');
      setShiftInfo(wData.worker.shift || '');

      // Load extra data if we have candidate_id
      if (wData.worker.candidate_id) {
        const [cData, fData, brData] = await Promise.all([
          api.get(`/candidates/${wData.worker.candidate_id}/comments`),
          api.get(`/candidates/${wData.worker.candidate_id}`), // To get files
          api.get(`/balance-requests/`)
        ]);
        setComments(cData.data);
        setCandidate((prev: any) => ({ ...prev, files: fData.data.files }));
        setBalanceRequests(brData.data.filter((r: any) => r.worker_id === wData.user_account?.id));
      }

      // Load attendance for target date
      const { data: attData } = await api.get('/attendance/', { params: { target_date: targetDate } });
      const att = attData.find((a: any) => a.worker_id === wData.worker.id);
      setAttendance(att || null);

    } catch (err: any) {
      if (err.response?.status === 404) {
        router.push('/dashboard/workers');
      }
    } finally {
      setLoading(false);
    }
  };"""

new_fetch = """  const fetchData = async () => {
    try {
      setLoading(true);
      const { data: workerData } = await api.get(`/workers/${id}`);
      setWorker(workerData);
      setAccountInfo(workerData.account_info || '');
      setShiftInfo(workerData.shift || '');

      // Fetch candidate
      const { data: candidateData } = await api.get(`/candidates/${workerData.candidate_id}`);
      setCandidate(candidateData);

      // Fetch admin user
      const { data: users } = await api.get('/users/');
      const adminUser = users.find((u: any) => u.id === workerData.admin_id);
      setAdmin(adminUser);

      // Find user account by candidate email
      const uAccount = users.find((u: any) => u.email === candidateData.email);
      setUserAccount(uAccount);

      // Fetch shift reports
      const { data: allReports } = await api.get('/shift-reports/');
      setReports(allReports.filter((r: any) => r.worker_id === workerData.id));

      // Extra data
      const [cData, brData, attData] = await Promise.all([
        api.get(`/candidates/${workerData.candidate_id}/comments`),
        api.get(`/balance-requests/`),
        api.get('/attendance/', { params: { target_date: targetDate } })
      ]);
      setComments(cData.data);
      if (uAccount) {
        setBalanceRequests(brData.data.filter((r: any) => r.worker_id === uAccount.id));
      }
      
      const att = attData.data.find((a: any) => a.worker_id === workerData.id);
      setAttendance(att || null);

    } catch (err: any) {
      console.error(err);
      if (err.response?.status === 404 || err.response?.status === 403) {
        router.push('/dashboard/workers');
      }
    } finally {
      setLoading(false);
    }
  };"""

content = content.replace(old_fetch, new_fetch)

with open("src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
