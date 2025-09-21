document.addEventListener("DOMContentLoaded", function () {
  var calendarEl = document.getElementById("calendar");
  var allEvents = [];

  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay",
    },
    events: [],
    editable: true,
    dateClick: function (info) {
      selectedDate = info.dateStr;
      document.getElementById("date_event").value = selectedDate;
      document.getElementById("date_diary").value = selectedDate;
      document.getElementById("date_image").value = selectedDate;
      document.getElementById("chooseModal").style.display = "block";
    },
  });

  calendar.render();

  // -------------------------
  // 載入事件 + 提醒功能
  // -------------------------
  function loadEvents() {
    fetch("/get_events")
      .then((res) => res.json())
      .then((data) => {
        allEvents = data;
        renderFilteredEvents();
        scheduleNotifications(data); // 🔔 加入提醒
      });
  }

  // -------------------------
  // 搜尋 + 篩選
  // -------------------------
  function renderFilteredEvents() {
    var searchText = document.getElementById("searchInput")?.value.toLowerCase() || "";
    var selectedTag = document.getElementById("tagFilter")?.value || "";

    var filtered = allEvents.filter((event) => {
      var matchSearch =
        event.title.toLowerCase().includes(searchText) ||
        (event.diary && event.diary.toLowerCase().includes(searchText));
      var matchTag = !selectedTag || event.tag === selectedTag;
      return matchSearch && matchTag;
    });

    calendar.removeAllEvents();
    calendar.addEventSource(filtered);
  }

  // 🔔 瀏覽器提醒
  function scheduleNotifications(events) {
    if (!("Notification" in window)) return;
    Notification.requestPermission();

    events.forEach((e) => {
      if (!e.start) return;
      let eventTime = new Date(e.start).getTime();
      let notifyTime = eventTime - 5 * 60 * 1000; // 提前5分鐘

      let now = new Date().getTime();
      if (notifyTime > now) {
        setTimeout(() => {
          new Notification("行事曆提醒", {
            body: `即將開始: ${e.title}`,
          });
        }, notifyTime - now);
      }
    });
  }

  // 監聽
  document.getElementById("searchInput")?.addEventListener("input", renderFilteredEvents);
  document.getElementById("tagFilter")?.addEventListener("change", renderFilteredEvents);

  loadEvents();
});
