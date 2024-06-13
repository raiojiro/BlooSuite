document.addEventListener("DOMContentLoaded", () => {
  const calendarContainer = document.getElementById("calendar");
  const selectedDateModal = new bootstrap.Modal(
    document.getElementById("selected-date-modal"),
  );
  const selectedDateModalTitle = document.getElementById(
    "selected-date-modal-title",
  );
  const selectedDateModalBody = document.getElementById(
    "selected-date-modal-body",
  );

  const addEventModalButton = document.getElementById("add-event-modal-button");
  const addEventModal = new bootstrap.Modal(
    document.getElementById("add-event-modal"),
  );
  const addEventModalTitle = document.getElementById("add-event-modal-title");
  const addEventModalBody = document.getElementById("add-event-modal-body");

  const allEvents = Array.from(document.querySelectorAll("[data-datetime]"));

  function selectDate(datetime) {
    selectedDateModalTitle.textContent = `Events for ${datetime.toLocaleString()}`;

    allEvents.forEach((value) => {
      const eventDateTime = luxon.DateTime.fromISO(
        value.getAttribute("data-datetime"),
      );

      if (
        datetime.startOf("day").toISODate() ===
        eventDateTime.startOf("day").toISODate()
      ) {
        value.removeAttribute("hidden");
      } else {
        value.setAttribute("hidden", "true");
      }
    });
    selectedDateModal.show();
  }

  function addEvent() {
    addEventModal.show();
  }

  addEventModalButton.onclick = addEvent;

  function renderCalendar(datetime) {
    for (let i = 0; i < datetime.daysInMonth; i++) {
      const div = document.createElement("div");

      const label = document.createElement("span");
      label.innerText = i + 1;

      const selectedDatetime = luxon.DateTime.fromObject({ day: i + 1 });

      div.onclick = () => {
        selectDate(selectedDatetime);
      };

      div.appendChild(label);

      calendarContainer.appendChild(div);
    }
  }

  const now = luxon.DateTime.now();
  renderCalendar(now);
});
