# Frontend Shifts Refactor Plan

1. Create Worker Page: `/dashboard/my-shifts`
   - Shows active shift status (button to Start or End).
   - If ending, shows a form to attach report data (screenshots, stats).
   - Lists history of their past shifts (`api.get('/shifts/my')`).

2. Create Admin Page: `/dashboard/shifts`
   - Tab 1: "Ожидают проверки" (Pending) -> lists shifts in PENDING_REVIEW (`api.get('/shifts/pending')`). Admin can view report and click "Approve".
   - Tab 2: "История смен" (History) -> lists all APPROVED/REJECTED shifts. (Needs an API endpoint for this).

3. Update Sidebar (`frontend/src/app/dashboard/layout.tsx`):
   - Admin: Replace 'Одобрение смен', 'Отчеты работников', 'Логи Работы' with a single 'Смены' -> `/dashboard/shifts`.
   - Worker: Replace 'Сдать смену' with 'Мои Смены' -> `/dashboard/my-shifts`.

4. Delete old pages:
   - `/dashboard/attendance`
   - `/dashboard/worker-reports`
   - `/dashboard/work-logs`
   - `/dashboard/shift-report`
