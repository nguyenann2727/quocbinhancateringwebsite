document.documentElement.classList.add("js-ready");

const header = document.querySelector(".site-header");
const menuButton = document.querySelector(".menu-toggle");
const mobileMenu = document.querySelector(".mobile-menu");
const navLinks = [...document.querySelectorAll(".desktop-nav a")];
const cursorGlow = document.querySelector(".cursor-glow");
const mobileMenuFocusable = [...mobileMenu.querySelectorAll("a, button:not([disabled])")];

document.querySelector("#year").textContent = new Date().getFullYear();

const sampleMenuSuite = document.querySelector(".qba-sample-menu-suite");
const budgetMenuSection = document.querySelector("#menu");
if (sampleMenuSuite && budgetMenuSection) {
  budgetMenuSection.insertAdjacentElement("afterend", sampleMenuSuite);
}

function syncHeader() {
  header.classList.toggle("scrolled", window.scrollY > 32);
}

syncHeader();
window.addEventListener("scroll", syncHeader, { passive: true });

function setMobileMenu(open, returnFocus = false) {
  const translate = window.QBA_I18N?.translate || ((value) => value);
  const sourceLabel = open ? "Đóng menu" : "Mở menu";
  menuButton.classList.toggle("active", open);
  mobileMenu.classList.toggle("open", open);
  document.body.classList.toggle("menu-open", open);
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.dataset.i18nSourceAriaLabel = sourceLabel;
  menuButton.setAttribute("aria-label", translate(sourceLabel));
  mobileMenu.setAttribute("aria-hidden", String(!open));
  if (open) mobileMenu.querySelector("a")?.focus();
  if (!open && returnFocus) menuButton.focus();
}

menuButton.addEventListener("click", () => setMobileMenu(!menuButton.classList.contains("active")));

mobileMenu.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => setMobileMenu(false));
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menuButton.classList.contains("active")) setMobileMenu(false, true);
  if (event.key !== "Tab" || !menuButton.classList.contains("active") || !mobileMenuFocusable.length) return;
  const first = mobileMenuFocusable[0];
  const last = mobileMenuFocusable[mobileMenuFocusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
});

const desktopHeaderQuery = window.matchMedia("(min-width: 1025px)");
desktopHeaderQuery.addEventListener?.("change", (event) => {
  if (event.matches && menuButton.classList.contains("active")) setMobileMenu(false);
});

const revealObserver = "IntersectionObserver" in window
  ? new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -30px" },
  )
  : null;

document.querySelectorAll(".reveal").forEach((element) => {
  if (revealObserver) revealObserver.observe(element);
  else element.classList.add("visible");
});

const sectionObserver = "IntersectionObserver" in window
  ? new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) return;
      navLinks.forEach((link) => {
        const isActive = link.getAttribute("href") === `#${visible.target.id}`;
        link.classList.toggle("active", isActive);
        if (isActive) link.setAttribute("aria-current", "page");
        else link.removeAttribute("aria-current");
      });
    },
    { threshold: [0.2, 0.45], rootMargin: "-15% 0px -55%" },
  )
  : null;

if (sectionObserver) {
  document
    .querySelectorAll("main section[id]")
    .forEach((section) => sectionObserver.observe(section));
}

function animateCounter(element) {
  const target = Number(element.dataset.count || 0);
  const duration = 1500;
  const startedAt = performance.now();

  function update(now) {
    const progress = Math.min((now - startedAt) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4);
    const current = Math.round(target * eased);
    element.textContent = new Intl.NumberFormat("vi-VN").format(current);
    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

const counterObserver = "IntersectionObserver" in window
  ? new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.65 },
  )
  : null;

document.querySelectorAll(".count").forEach((counter) => {
  if (counterObserver) counterObserver.observe(counter);
  else counter.textContent = new Intl.NumberFormat("vi-VN").format(Number(counter.dataset.count || 0));
});

// Thực đơn mẫu theo mức giá và ngày; thay món tại đây khi có lịch bếp chính thức.
const CONTENT_STORAGE_KEY = "qba-content-editor-v1";
const productionContentRecords = window.QBA_DRAFT_FINAL?.contentRecords || {};
const menuDayOrder = ["mon", "tue", "wed", "thu", "fri", "sat"];
const menuSampleLabels = { mon: "MẪU 01", tue: "MẪU 02", wed: "MẪU 03", thu: "MẪU 04", fri: "MẪU 05", sat: "MẪU 06" };
const menuDayNames = { mon: "THỨ 2", tue: "THỨ 3", wed: "THỨ 4", thu: "THỨ 5", fri: "THỨ 6", sat: "THỨ 7" };
const menuDayRepresentativeImages = {
  basic: {
    mon: "assets/menu/qba-23k-actual-mon-20260801.jpg",
    tue: "assets/menu/qba-23k-actual-tue-20260801.jpg",
    wed: "assets/menu/qba-23k-actual-wed-20260801.jpg",
    thu: "assets/menu/qba-23k-actual-thu-20260801.jpg",
    fri: "assets/menu/qba-23k-actual-fri-20260801.jpg",
    sat: "assets/menu/qba-23k-actual-sat-20260801.jpg",
  },
  standard: {
    mon: "assets/menu/qba-24k-actual-sample-01-web.jpg",
    tue: "assets/menu/qba-24k-actual-sample-02-web.jpg",
    wed: "assets/menu/qba-24k-actual-sample-03-web.jpg",
    thu: "assets/menu/qba-24k-actual-sample-04-web.jpg",
    fri: "assets/menu/qba-24k-actual-sample-05-web.jpg",
    sat: "assets/menu/qba-24k-actual-sample-06-web.jpg",
  },
  energy: {
    mon: "assets/menu/qba-25k-actual-mon.jpg",
    tue: "assets/menu/qba-25k-actual-tue.jpg",
    wed: "assets/menu/qba-25k-actual-wed.jpg",
    thu: "assets/menu/qba-25k-actual-thu.jpg",
    fri: "assets/menu/qba-25k-actual-fri.jpg",
    sat: "assets/menu/qba-25k-actual-sat.jpg",
  },
  premium: {
    mon: "assets/menu/qba-40k-chinese-mon.jpg",
    tue: "assets/menu/qba-40k-chinese-tue.jpg",
    wed: "assets/menu/qba-40k-chinese-wed.jpg",
    thu: "assets/menu/qba-40k-chinese-thu.jpg",
    fri: "assets/menu/qba-40k-chinese-fri.jpg",
    sat: "assets/menu/qba-40k-chinese-sat.jpg",
  },
  light: {
    mon: "assets/menu/qba-expert-mon-table-v3-20260805-web.jpg",
    tue: "assets/menu/qba-expert-tue-table-v3-20260805-web.jpg",
    wed: "assets/menu/qba-expert-wed-table-v3-20260805-web.jpg",
    thu: "assets/menu/qba-expert-thu-table-v3-20260805-web.jpg",
    fri: "assets/menu/qba-expert-fri-table-v3-20260805-web.jpg",
    sat: "assets/menu/qba-expert-sat-table-v3-20260805-web.jpg",
  },
};
const menus = {
  basic: {
    code: "SUẤT 23.000Đ",
    price: "23.000Đ",
    days: {
      mon: { dishes: [["Bò xào đậu que", "Trưa · Món mặn"], ["Cá thu kho cà", "Trưa · Món mặn"], ["Tôm rim", "Trưa · Món mặn"], ["Cà tím kho", "Trưa · Món phụ"], ["Táo xanh", "Trưa · Trái cây"]] },
      tue: { dishes: [["Gà chiên giòn", "Trưa · Món mặn"], ["Thịt heo xào ớt chuông", "Trưa · Xào phụ"], ["Cà tím kho", "Trưa · Món phụ"], ["Táo xanh", "Trưa · Trái cây"]] },
      wed: { dishes: [["Khổ qua nhồi thịt", "Trưa · Món mặn"], ["Cá thu kho cà", "Trưa · Món mặn"], ["Rau muống xào tỏi", "Trưa · Rau xào"], ["Nhãn", "Trưa · Trái cây"]] },
      thu: { dishes: [["Cá nục chiên sả ớt", "Trưa · Món mặn"], ["Khổ qua xào thịt heo", "Trưa · Xào phụ"], ["Cải thảo luộc", "Trưa · Rau"], ["Táo xanh", "Trưa · Trái cây"]] },
      fri: { dishes: [["Tàu hũ ky kho", "Trưa · Món phụ"], ["Ba rọi kho mè", "Trưa · Món mặn"], ["Rau muống xào tỏi", "Trưa · Rau xào"], ["Nhãn", "Trưa · Trái cây"]] },
      sat: { dishes: [["Khổ qua xào trứng", "Trưa · Món phụ"], ["Thịt heo xào tôm", "Trưa · Món mặn"], ["Bắp cải luộc", "Trưa · Rau"], ["Ổi xanh", "Trưa · Trái cây"]] },
    },
  },
  standard: {
    code: "SUẤT 24.000Đ",
    price: "24.000Đ",
    days: {
      mon: { dishes: [["Cơm trắng", "Trưa · Cơm"], ["Xíu mại sốt cà chua", "Trưa · Món mặn"], ["Tôm rim mặn ngọt", "Trưa · Món mặn"], ["Bắp cải xào cà rốt", "Trưa · Rau xào"], ["Canh bí đỏ thịt bằm", "Trưa · Canh"]] },
      tue: { dishes: [["Cơm trắng", "Trưa · Cơm"], ["Cá kho măng", "Trưa · Món mặn"], ["Bò xào đậu que", "Trưa · Xào phụ"], ["Bắp cải xào cà rốt", "Trưa · Rau xào"], ["Canh bí đỏ", "Trưa · Canh"]] },
      wed: { dishes: [["Cơm trắng", "Trưa · Cơm"], ["Gà kho gừng", "Trưa · Món mặn"], ["Cá chiên sả ớt", "Trưa · Món mặn"], ["Su su xào tỏi", "Trưa · Rau xào"], ["Canh bí xanh hành lá", "Trưa · Canh"]] },
      thu: { dishes: [["Cơm trắng", "Trưa · Cơm"], ["Cá chiên giòn", "Trưa · Món mặn"], ["Thịt heo xào hành tây cà rốt", "Trưa · Xào phụ"], ["Rau muống xào tỏi", "Trưa · Rau xào"], ["Canh khoai mỡ", "Trưa · Canh"]] },
      fri: { dishes: [["Cơm trắng", "Trưa · Cơm"], ["Thịt heo xào thơm", "Trưa · Món mặn"], ["Thịt heo xào sả ớt", "Trưa · Xào phụ"], ["Bắp cải xào cà rốt", "Trưa · Rau xào"], ["Canh cải xanh", "Trưa · Canh"]] },
      sat: { dishes: [["Cơm trắng", "Trưa · Cơm"], ["Chả cá kho thơm", "Trưa · Món mặn"], ["Ba rọi kho tiêu", "Trưa · Món mặn"], ["Canh rau ngót", "Trưa · Canh"], ["Đu đủ chín", "Trưa · Trái cây"]] },
    },
  },
  energy: {
    code: "SUẤT 25.000Đ",
    price: "25.000Đ",
    days: {
      mon: { dishes: [["Đùi gà nướng", "Trưa · Món mặn"], ["Đậu hũ kho hành", "Trưa · Xào phụ"], ["Dưa leo", "Trưa · Rau"], ["Canh bí đao", "Trưa · Canh"], ["Dưa hấu", "Trưa · Trái cây"]] },
      tue: { dishes: [["Cá chiên sả ớt", "Trưa · Món mặn"], ["Bò xào rau cải", "Trưa · Xào phụ"], ["Dưa leo", "Trưa · Rau"], ["Canh bầu thịt bằm", "Trưa · Canh"]] },
      wed: { dishes: [["Cá kèo kho tiêu", "Trưa · Món mặn"], ["Trứng chiên", "Trưa · Xào phụ"], ["Su su xào", "Trưa · Rau xào"], ["Canh rau ngót", "Trưa · Canh"], ["Chuối", "Trưa · Trái cây"]] },
      thu: { dishes: [["Cá nục kho tiêu", "Trưa · Món mặn"], ["Thịt heo xào hành tây", "Trưa · Xào phụ"], ["Su su xào cà rốt", "Trưa · Rau xào"], ["Mận đỏ", "Trưa · Trái cây"]] },
      fri: { dishes: [["Cá nục sốt cà", "Trưa · Món mặn"], ["Thịt heo xào", "Trưa · Xào phụ"], ["Rau muống xào tỏi", "Trưa · Rau xào"], ["Canh rau ngót thịt bằm", "Trưa · Canh"], ["Chôm chôm", "Trưa · Trái cây"]] },
      sat: { dishes: [["Sườn non kho / Cá kho cà chua", "Trưa · Món mặn"], ["Trứng ốp la", "Trưa · Xào phụ"], ["Cải thìa luộc", "Trưa · Rau"], ["Táo xanh", "Trưa · Trái cây"]] },
    },
  },
  premium: {
    code: "SUẤT 40.000Đ",
    price: "40.000Đ",
    days: {
      mon: { dishes: [["Tôm rim xì dầu kiểu Hoa", "Trưa · Món mặn"], ["Gà kho nấm đông cô", "Trưa · Món mặn"], ["Bò xào ớt xanh", "Trưa · Xào phụ"], ["Giá hẹ xào tỏi", "Trưa · Rau xào"], ["Dưa hấu", "Trưa · Trái cây"]] },
      tue: { dishes: [["Thịt viên sốt tương kiểu Hoa", "Trưa · Món mặn"], ["Gà kho nấm", "Trưa · Món mặn"], ["Bò xào ớt chuông", "Trưa · Xào phụ"], ["Bắp cải xào xì dầu", "Trưa · Rau xào"], ["Chôm chôm", "Trưa · Trái cây"]] },
      wed: { dishes: [["Bò sốt tỏi kiểu Hoa", "Trưa · Món mặn"], ["Sườn xào chua ngọt rắc mè", "Trưa · Món mặn"], ["Bò xào ớt xanh", "Trưa · Xào phụ"], ["Cải thảo xào xì dầu", "Trưa · Rau xào"], ["Chôm chôm", "Trưa · Trái cây"]] },
      thu: { dishes: [["Cá chiên ngũ vị", "Trưa · Món mặn"], ["Gà xào sốt cay", "Trưa · Món mặn"], ["Bò xào ớt chuông", "Trưa · Xào phụ"], ["Cải xanh xào dầu hào", "Trưa · Rau xào"], ["Nhãn", "Trưa · Trái cây"]] },
      fri: { dishes: [["Gà chiên giòn xào sả ớt", "Trưa · Món mặn"], ["Thịt kho nấm đông cô", "Trưa · Món mặn"], ["Trứng xào ớt xanh", "Trưa · Xào phụ"], ["Đậu bắp xào tỏi", "Trưa · Rau xào"], ["Dưa hấu", "Trưa · Trái cây"]] },
      sat: { dishes: [["Cá hấp sốt ớt tỏi kiểu Hồ Nam", "Trưa · Món mặn"], ["Sườn sốt chua ngọt rắc mè", "Trưa · Món mặn"], ["Trứng xào hẹ", "Trưa · Xào phụ"], ["Rau muống xào tỏi", "Trưa · Rau xào"], ["Dưa hấu", "Trưa · Trái cây"]] },
    },
  },
  light: {
    code: "SUẤT CHUYÊN GIA 45.000–50.000Đ",
    price: "45.000–50.000Đ",
    serviceQuantity: "Số lượng khách phục vụ: 6 người / 1 bàn ăn",
    days: {
      mon: { dishes: [["Cá hấp xì dầu hành gừng", "Trưa · Món mặn"], ["Ba chỉ rang xì dầu", "Trưa · Món mặn"], ["Mực xào sa tế hành tỏi", "Trưa · Xào phụ"], ["Đậu hũ Ma Bà", "Trưa · Món phụ"], ["Cải ngọt xào tỏi", "Trưa · Rau xào"], ["Canh rong biển trứng", "Trưa · Canh"]] },
      tue: { dishes: [["Cá chiên sốt xì dầu", "Trưa · Món mặn"], ["Gà quay ngũ vị", "Trưa · Món mặn"], ["Tôm rang muối kiểu Hoa", "Trưa · Món phụ"], ["Thịt heo xào hành tây", "Trưa · Xào phụ"], ["Cải bó xôi xào tỏi", "Trưa · Rau xào"], ["Canh củ cải hầm", "Trưa · Canh"]] },
      wed: { dishes: [["Cá kho nấm đông cô", "Trưa · Món mặn"], ["Thịt kho tàu kiểu Hoa", "Trưa · Món mặn"], ["Gà hấp hành", "Trưa · Món phụ"], ["Măng xào thịt heo", "Trưa · Xào phụ"], ["Cải thìa xào tỏi", "Trưa · Rau xào"], ["Canh cà chua trứng", "Trưa · Canh"]] },
      thu: { dishes: [["Cá hấp xì dầu hành gừng", "Trưa · Món mặn"], ["Giò heo kho măng khô", "Trưa · Món mặn"], ["Bò xào giá hẹ", "Trưa · Xào phụ"], ["Bông cải xào nấm", "Trưa · Món phụ"], ["Cải ngọt xào tỏi", "Trưa · Rau xào"], ["Canh cải xanh", "Trưa · Canh"]] },
      fri: { dishes: [["Bò hầm cà rốt kiểu Hoa", "Trưa · Món mặn"], ["Gà chiên giòn tỏi", "Trưa · Món mặn"], ["Cá phi lê chiên giòn", "Trưa · Món phụ"], ["Trứng chiên hành kiểu Hoa", "Trưa · Xào phụ"], ["Cải thảo xào dầu hào", "Trưa · Rau xào"], ["Canh rong biển đậu hũ", "Trưa · Canh"]] },
      sat: { dishes: [["Cá hấp xì dầu hành gừng", "Trưa · Món mặn"], ["Ba chỉ kho tàu kiểu Hoa", "Trưa · Món mặn"], ["Bò xào ớt xanh tiêu đen", "Trưa · Xào phụ"], ["Trứng xào hành tây", "Trưa · Món phụ"], ["Rau muống xào tỏi", "Trưa · Rau xào"], ["Canh bí đao hầm xương", "Trưa · Canh"]] },
    },
  },
};

const menuTranslationAuditValues = [...new Set(Object.values(menus).flatMap((tier) => (
  Object.values(tier.days).flatMap((day) => day.dishes.flat())
)))];
const menuTranslationAudit = window.QBA_I18N?.auditMenuStrings?.(menuTranslationAuditValues) || {};
const missingMenuTranslations = Object.entries(menuTranslationAudit).flatMap(([language, values]) => (
  values.map((value) => `${language}: ${value}`)
));
if (missingMenuTranslations.length) {
  console.error("[QBA menu i18n] Missing exact translations:", missingMenuTranslations);
}

const menuCode = document.querySelector("#menu-code");
const menuSampleLabel = document.querySelector("#menu-sample-label");
const menuServiceQuantity = document.querySelector("#menu-service-quantity");
const menuDayLabel = document.querySelector("#menu-day-label");
const menuDishes = document.querySelector("#menu-dishes");
const menuBoard = document.querySelector(".menu-board");
const menuDayRepresentative = document.querySelector("#menu-day-representative");
const menuDayRepresentativeTitle = document.querySelector("#menu-day-representative-title");
const menuDayRepresentativePhoto = document.querySelector("#menu-day-representative-photo");
const menuWeekGallery = document.querySelector("#menu-week-gallery");
const menuWeekGalleryGrid = document.querySelector("#menu-week-gallery-grid");
const menuImagePrice = document.querySelector("#menu-image-price");
const menuImageLabel = document.querySelector("#menu-image-label");
const menuPanel = document.querySelector("#menu-panel");
const menuTabs = [...document.querySelectorAll(".menu-tab")];
const menuDayButtons = [...document.querySelectorAll(".menu-day")];
const menuDayPrev = document.querySelector("#menu-day-prev");
const menuDayNext = document.querySelector("#menu-day-next");
const menuSlidePrev = document.querySelector(".menu-slide-prev");
const menuSlideNext = document.querySelector(".menu-slide-next");
let currentMenuTier = "basic";
let currentMenuDay = "mon";

function getCurrentMenu() {
  const tier = menus[currentMenuTier];
  const day = tier?.days[currentMenuDay];
  return tier && day ? { ...day, code: tier.code, price: tier.price } : null;
}

function escapeMenuHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function sanitizeMenuEditableHtml(html) {
  const template = document.createElement("template");
  template.innerHTML = String(html ?? "");
  const allowedTags = new Set(["BR", "SPAN", "STRONG", "SMALL", "EM", "B", "I"]);
  [...template.content.querySelectorAll("*")].forEach((node) => {
    if (["SCRIPT", "STYLE", "IFRAME", "OBJECT", "EMBED", "FORM", "INPUT", "BUTTON"].includes(node.tagName)) {
      node.remove();
      return;
    }
    if (!allowedTags.has(node.tagName)) {
      node.replaceWith(...node.childNodes);
      return;
    }
    [...node.attributes].forEach((attribute) => node.removeAttribute(attribute.name));
  });
  return template.innerHTML.trim();
}

function translateEditableMenuHtml(html) {
  const translate = window.QBA_I18N?.translateExact || window.QBA_I18N?.translate;
  if (!translate || !html) return html;
  const template = document.createElement("template");
  template.innerHTML = html;
  const walker = document.createTreeWalker(template.content, NodeFilter.SHOW_TEXT);
  let textNode = walker.nextNode();
  while (textNode) {
    if (textNode.nodeValue.trim()) textNode.nodeValue = translate(textNode.nodeValue);
    textNode = walker.nextNode();
  }
  return template.innerHTML;
}

function getStoredMenuContentHtml(key, fallbackText) {
  try {
    const records = JSON.parse(localStorage.getItem(CONTENT_STORAGE_KEY) || "{}");
    const record = records?.[key] || productionContentRecords[key];
    if (record?.html !== undefined) return translateEditableMenuHtml(sanitizeMenuEditableHtml(record.html));
  } catch (error) {
    // Nếu trình duyệt chặn lưu trữ, website vẫn hiển thị nội dung mặc định.
  }
  return translateEditableMenuHtml(escapeMenuHtml(fallbackText));
}

function normalizeMenuLineStarts(root = document) {
  const language = document.documentElement.lang || "vi";
  root.querySelectorAll(".qba-sample-menu-table tbody th, .qba-sample-menu-table tbody td, #menu-dishes strong").forEach((container) => {
    const nodes = [...container.childNodes];
    while (nodes.length) {
      const node = nodes.shift();
      if (node.nodeType === Node.TEXT_NODE) {
        node.nodeValue = node.nodeValue.replace(/^(\s*)(\p{L})/u, (_, spacing, letter) => (
          `${spacing}${letter.toLocaleUpperCase(language)}`
        ));
      } else if (node.childNodes?.length) {
        nodes.unshift(...node.childNodes);
      }
    }
  });
}

function isLunchDishGroup(group, dishes) {
  const value = String(group || "").trim();
  const hasExplicitLunch = dishes.some(([, itemGroup]) => /^Trưa\b/i.test(String(itemGroup || "").trim()));
  if (hasExplicitLunch) return /^Trưa\b/i.test(value);
  return !/^(Chiều|Tăng ca|Ca chiều|Ca tối|Tối|Khuya|Đêm)\b/i.test(value);
}

function syncMenuDishEditables() {
  if (!document.body.classList.contains("content-edit-mode")) return;
  menuDishes.querySelectorAll("[data-content-editable]").forEach((element) => {
    element.setAttribute("contenteditable", "true");
    element.setAttribute("spellcheck", "true");
  });
}

function renderMenu(menu) {
  const translate = window.QBA_I18N?.translate || ((value) => value);
  const translateExact = window.QBA_I18N?.translateExact || translate;
  const dayName = menuDayNames[currentMenuDay];
  const sampleLabel = menuSampleLabels[currentMenuDay];
  const representativeSlotId = `menu-week-${currentMenuTier}-${currentMenuDay}`;
  const customRepresentative = window.__qbaImageEditorReady ? imageRecords.get(representativeSlotId) : null;
  const representativeImage = customRepresentative?.dataUrl || menuDayRepresentativeImages[currentMenuTier]?.[currentMenuDay];
  menuCode.textContent = translate(menu.code);
  menuSampleLabel.textContent = `${translate(dayName)} · ${translate(sampleLabel)} / 06`;
  if (menuServiceQuantity) {
    const serviceQuantity = menus[currentMenuTier]?.serviceQuantity || "";
    menuServiceQuantity.textContent = translate(serviceQuantity);
    menuServiceQuantity.hidden = !serviceQuantity;
  }
  menuDayLabel.textContent = `${translate(dayName)} · ${translate(sampleLabel)}`;
  menuImagePrice.textContent = translate(menu.price);
  menuImageLabel.textContent = `${translate(sampleLabel)} / 06`;
  if (menuBoard) menuBoard.dataset.menuTier = currentMenuTier;
  menuBoard?.classList.toggle("has-representative-image", Boolean(representativeImage));
  if (menuDayRepresentative && menuDayRepresentativePhoto) {
    menuDayRepresentative.hidden = !representativeImage;
    if (representativeImage) {
      const tierLabel = menuTierLabels[currentMenuTier] || menu.code;
      if (menuDayRepresentativeTitle) menuDayRepresentativeTitle.textContent = `${translate(dayName)} · ${translate(tierLabel)}`;
      menuDayRepresentativePhoto.style.backgroundImage = `url("${representativeImage}")`;
      const representativeLabel = `Ảnh đại diện suất ăn theo ngày · ${dayName} · ${tierLabel}`;
      menuDayRepresentativePhoto.dataset.i18nSourceAriaLabel = representativeLabel;
      menuDayRepresentativePhoto.setAttribute("aria-label", translate(representativeLabel));
    } else {
      menuDayRepresentativePhoto.style.removeProperty("background-image");
      delete menuDayRepresentativePhoto.dataset.i18nSourceAriaLabel;
      menuDayRepresentativePhoto.removeAttribute("aria-label");
    }
  }
  const emptyMenuHelper = currentMenuTier === "energy"
    ? "Phần 25K đang để trống theo yêu cầu, chờ thực đơn và ảnh chính thức."
    : "Ảnh và đơn giá vẫn có thể xem ở khung bên dưới.";
  const lunchDishes = menu.dishes.filter(([, group]) => isLunchDishGroup(group, menu.dishes));
  menuDishes.innerHTML = lunchDishes.length
    ? lunchDishes.map(([dish, group], index) => {
      const dishText = translateExact(dish);
      const groupText = translateExact(group);
      const dishKey = `menu-${currentMenuTier}-${currentMenuDay}-dish-${String(index + 1).padStart(2, "0")}`;
      const groupKey = `menu-${currentMenuTier}-${currentMenuDay}-group-${String(index + 1).padStart(2, "0")}`;
      return `
      <div>
        <span>${String(index + 1).padStart(2, "0")}</span>
        <strong data-i18n-exact data-content-editable="true" data-content-key="${dishKey}" data-content-original="${escapeMenuHtml(dishText)}">${getStoredMenuContentHtml(dishKey, dishText)}</strong>
        <small data-i18n-exact data-content-editable="true" data-content-key="${groupKey}" data-content-original="${escapeMenuHtml(groupText)}">${getStoredMenuContentHtml(groupKey, groupText)}</small>
      </div>`;
    }).join("")
    : `<div class="menu-empty-note"><strong>${translate("Đang cập nhật thực đơn chi tiết")}</strong><small>${translate(emptyMenuHelper)}</small></div>`;
  syncMenuDishEditables();
  normalizeMenuLineStarts(menuDishes);
  renderMenuWeekGallery(translate);
}

function renderMenuWeekGallery(translate) {
  if (!menuWeekGallery || !menuWeekGalleryGrid) return;
  const images = menuDayRepresentativeImages[currentMenuTier];
  const visibleDays = currentMenuTier === "basic" && images
    ? menuDayOrder
    : images ? menuDayOrder.filter((day) => Boolean(images[day])) : [];
  const shouldShowGallery = visibleDays.length > 0;
  menuWeekGallery.hidden = !shouldShowGallery;
  menuWeekGallery.classList.toggle("is-active", shouldShowGallery);
  if (!shouldShowGallery) {
    menuWeekGalleryGrid.innerHTML = "";
    return;
  }

  const tierLabel = menuTierLabels[currentMenuTier] || menus[currentMenuTier]?.code || "";
  const galleryTitle = menuWeekGallery.querySelector(".menu-week-gallery-copy strong");
  const galleryNote = menuWeekGallery.querySelector(".menu-week-gallery-copy small");
  if (galleryTitle) {
    galleryTitle.textContent = currentMenuTier === "basic"
      ? translate("Ảnh V3 đã xác nhận theo thứ trong tuần")
      : translate("Đủ 6 mẫu từ Thứ 2 đến Thứ 7");
  }
  if (galleryNote) {
    galleryNote.textContent = currentMenuTier === "basic"
      ? translate("Chỉ hiển thị ảnh 23K đã được ghép đúng, không dùng lại ảnh cũ để tránh sai món.")
      : translate("Bấm vào từng khay để xem món tương ứng trong lịch mẫu.");
  }

  menuWeekGalleryGrid.innerHTML = visibleDays.map((day) => {
    const dayName = menuDayNames[day];
    const sampleLabel = menuSampleLabels[day];
    const image = images[day];
    const isActive = day === currentMenuDay;
    const slotId = `menu-week-${currentMenuTier}-${day}`;
    const slotLabel = `Ảnh lịch thực đơn ${tierLabel} - ${dayName}`;
    const imageAriaLabel = `${tierLabel} · ${dayName} · ${sampleLabel}`;
    const imageMarkup = image
      ? `<span class="editable-frame menu-week-gallery-photo has-default-image" data-image-slot="${slotId}" data-image-label="${escapeMenuHtml(slotLabel)}" data-i18n-source-aria-label="${escapeMenuHtml(imageAriaLabel)}" data-image-mode="frame" data-image-fit="contain" data-menu-week-default-image="${escapeMenuHtml(image)}" aria-label="${escapeMenuHtml(imageAriaLabel)}"></span>`
      : `<span class="editable-frame menu-week-gallery-photo is-empty" data-image-slot="${slotId}" data-image-label="${escapeMenuHtml(slotLabel)}" data-image-mode="frame" data-image-fit="contain"><em>${translate("Chờ ảnh V3")}</em></span>`;
    return `
      <article class="menu-week-gallery-card${isActive ? " active" : ""}${image ? "" : " is-empty"}" role="button" tabindex="0" data-week-menu-day="${day}" aria-pressed="${String(isActive)}">
        ${imageMarkup}
        <span class="menu-week-gallery-day">${translate(dayName)}</span>
        <strong>${translate(sampleLabel)} / 06</strong>
      </article>`;
  }).join("");
  menuWeekGalleryGrid.querySelectorAll("[data-menu-week-default-image]").forEach((element) => {
    element.style.setProperty("--menu-week-image", `url("${element.dataset.menuWeekDefaultImage}")`);
  });
  if (window.__qbaImageEditorReady) {
    registerImageSlots(menuWeekGalleryGrid);
    imageRecords.forEach(applyImageRecord);
    renderImageManager();
  }
}

function updateMenuDisplay() {
  const menu = getCurrentMenu();
  if (!menu) return;
  const photoStack = menuPanel.querySelector(".menu-photo-stack");
  if (photoStack) photoStack.dataset.editMenuTier = currentMenuTier;

  menuDayButtons.forEach((button) => {
    const isActive = button.dataset.menuDay === currentMenuDay;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", String(isActive));
    button.tabIndex = isActive ? 0 : -1;
    if (isActive) menuDishes.setAttribute("aria-labelledby", button.id);
  });

  document.querySelectorAll(".menu-photo-frame").forEach((photo) => {
    photo.classList.toggle("active", photo.dataset.menuPhoto === `${currentMenuTier}-${currentMenuDay}`);
  });
  const activePhoto = menuPanel.querySelector(".menu-photo-frame.active");
  if (activePhoto) ensureDefaultMenuImage(activePhoto.dataset.imageSlot, menuPanel);
  if (document.body.classList.contains("image-edit-mode")) ensureDefaultMenuImagesForTier(currentMenuTier, menuPanel);
  syncMenuPhotoState();
  renderMenu(menu);
}

function activateMenu(tab, moveFocus = false) {
  if (!menus[tab.dataset.menu]) return;
  currentMenuTier = tab.dataset.menu;

  menuTabs.forEach((button) => {
    const isActive = button === tab;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", String(isActive));
    button.tabIndex = isActive ? 0 : -1;
  });
  menuPanel.setAttribute("aria-labelledby", tab.id);
  if (moveFocus) tab.focus();
  updateMenuDisplay(1);
}

function activateMenuDay(day, moveFocus = false, directionOverride = null) {
  const nextIndex = menuDayOrder.indexOf(day);
  const currentIndex = menuDayOrder.indexOf(currentMenuDay);
  if (nextIndex < 0) return;
  const direction = directionOverride ?? (nextIndex >= currentIndex ? 1 : -1);
  currentMenuDay = day;
  updateMenuDisplay(direction);
  if (moveFocus) menuDayButtons[nextIndex]?.focus();
}

menuTabs.forEach((tab) => {
  tab.addEventListener("click", () => activateMenu(tab));
  tab.addEventListener("keydown", (event) => {
    const currentIndex = menuTabs.indexOf(tab);
    let nextIndex = null;
    if (event.key === "ArrowRight") nextIndex = (currentIndex + 1) % menuTabs.length;
    if (event.key === "ArrowLeft") nextIndex = (currentIndex - 1 + menuTabs.length) % menuTabs.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = menuTabs.length - 1;
    if (nextIndex === null) return;
    event.preventDefault();
    activateMenu(menuTabs[nextIndex], true);
  });
});

menuDayPrev.addEventListener("click", () => {
  const index = menuDayOrder.indexOf(currentMenuDay);
  activateMenuDay(menuDayOrder[(index - 1 + menuDayOrder.length) % menuDayOrder.length], false, -1);
});

menuDayNext.addEventListener("click", () => {
  const index = menuDayOrder.indexOf(currentMenuDay);
  activateMenuDay(menuDayOrder[(index + 1) % menuDayOrder.length], false, 1);
});

menuSlidePrev.addEventListener("click", () => menuDayPrev.click());
menuSlideNext.addEventListener("click", () => menuDayNext.click());

menuDayButtons.forEach((button) => {
  button.addEventListener("click", () => activateMenuDay(button.dataset.menuDay));
  button.addEventListener("keydown", (event) => {
    const currentIndex = menuDayButtons.indexOf(button);
    let nextIndex = null;
    if (event.key === "ArrowRight") nextIndex = (currentIndex + 1) % menuDayButtons.length;
    if (event.key === "ArrowLeft") nextIndex = (currentIndex - 1 + menuDayButtons.length) % menuDayButtons.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = menuDayButtons.length - 1;
    if (nextIndex === null) return;
    event.preventDefault();
    activateMenuDay(menuDayButtons[nextIndex].dataset.menuDay, true);
  });
});
menuWeekGalleryGrid?.addEventListener("click", (event) => {
  const card = event.target.closest("[data-week-menu-day]");
  if (!card) return;
  if (document.body.classList.contains("image-edit-mode") && event.target.closest("[data-image-slot]")) return;
  activateMenuDay(card.dataset.weekMenuDay);
});
menuWeekGalleryGrid?.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  const card = event.target.closest("[data-week-menu-day]");
  if (!card) return;
  event.preventDefault();
  activateMenuDay(card.dataset.weekMenuDay);
});
document.addEventListener("qba:languagechange", updateMenuDisplay);

let menuSwipeStartX = null;
menuPanel.addEventListener("pointerdown", (event) => {
  if (event.pointerType !== "touch" || document.body.classList.contains("image-edit-mode")) return;
  menuSwipeStartX = event.clientX;
});
menuPanel.addEventListener("pointerup", (event) => {
  if (menuSwipeStartX === null) return;
  const distance = event.clientX - menuSwipeStartX;
  menuSwipeStartX = null;
  if (Math.abs(distance) < 55) return;
  const index = menuDayOrder.indexOf(currentMenuDay);
  const direction = distance < 0 ? 1 : -1;
  const nextIndex = (index + direction + menuDayOrder.length) % menuDayOrder.length;
  activateMenuDay(menuDayOrder[nextIndex], false, direction);
});
menuPanel.addEventListener("pointercancel", () => { menuSwipeStartX = null; });

const menuGallery = document.querySelector("#menu-gallery");
const menuGalleryGrid = document.querySelector("#menu-gallery-grid");
const menuGalleryToggle = document.querySelector("#menu-gallery-toggle");
const menuGalleryClose = document.querySelector("#menu-gallery-close");
const menuQuote = document.querySelector("#menu-quote");
const menuTierLabels = { basic: "Suất 23K", standard: "Suất 24K", energy: "Suất 25K", premium: "Suất 40K", light: "45–50K · Chuyên gia" };
const menuTierPrices = { basic: "23.000đ", standard: "24.000đ", energy: "25.000đ", premium: "40.000đ", light: "45.000–50.000đ" };
const menuDefaultImages = {
  "menu-basic-mon": "assets/menu/qba-23k-actual-gallery-mon-20260803.png",
  "menu-basic-tue": "assets/menu/qba-23k-actual-gallery-tue-20260803.png",
  "menu-basic-wed": "assets/menu/qba-23k-actual-gallery-wed-20260803.png",
  "menu-basic-thu": "assets/menu/qba-23k-actual-gallery-thu-20260803.png",
  "menu-basic-fri": "assets/menu/qba-23k-actual-gallery-fri-20260803.png",
  "menu-basic-sat": "assets/menu/qba-23k-actual-gallery-sat-20260803.png",
  "menu-standard-mon": "assets/menu-24k-real-pro-01.jpg",
  "menu-standard-tue": "assets/menu-24k-real-pro-02.jpg",
  "menu-standard-wed": "assets/menu-24k-real-pro-03.jpg",
  "menu-standard-thu": "assets/menu-24k-real-pro-04.jpg",
  "menu-standard-fri": "assets/menu-24k-real-pro-05.jpg",
  "menu-standard-sat": "assets/menu-24k-real-pro-06.jpg",
  "menu-energy-mon": "assets/menu/qba-25k-actual-mon-gallery-landscape.jpg",
  "menu-energy-tue": "assets/menu/qba-25k-actual-tue-gallery-landscape.jpg",
  "menu-energy-wed": "assets/menu/qba-25k-actual-wed-gallery-landscape.jpg",
  "menu-energy-thu": "assets/menu/qba-25k-actual-thu-gallery-landscape.jpg",
  "menu-energy-fri": "assets/menu/qba-25k-actual-fri-gallery-landscape.jpg",
  "menu-energy-sat": "assets/menu/qba-25k-actual-sat-gallery-landscape.jpg",
  "menu-premium-mon": "assets/menu/qba-40k-chinese-mon-gallery-landscape.jpg",
  "menu-premium-tue": "assets/menu/qba-40k-chinese-tue-gallery-landscape.jpg",
  "menu-premium-wed": "assets/menu/qba-40k-chinese-wed-gallery-landscape.jpg",
  "menu-premium-thu": "assets/menu/qba-40k-chinese-thu-gallery-landscape.jpg",
  "menu-premium-fri": "assets/menu/qba-40k-chinese-fri-gallery-landscape.jpg",
  "menu-premium-sat": "assets/menu/qba-40k-chinese-sat-gallery-landscape.jpg",
  "menu-light-mon": "assets/menu-45-50k-sample-01.jpg",
  "menu-light-tue": "assets/menu-45-50k-sample-02.jpg",
  "menu-light-wed": "assets/menu-45-50k-sample-03.jpg",
  "menu-light-thu": "assets/menu-50k-pro-01.jpg",
  "menu-light-fri": "assets/menu-50k-pro-02.jpg",
  "menu-light-sat": "assets/menu-50k-pro-03.jpg",
};
const partnerDefaultImages = {
  "partner-01": "assets/partner-e-top.webp",
  "partner-02": "assets/partner-twinkle.webp",
  "partner-03": "assets/partner-hoang-gia.png",
  "partner-04": "assets/partner-jys.jpeg",
  "partner-05": "assets/partner-bellinturf.jpeg",
  "partner-06": "assets/partner-jintian.png",
  "partner-07": "assets/partner-leow-foods.jpg",
  "partner-08": "assets/partner-tah-tong.webp",
  "partner-09": "assets/partner-minh-tri.webp",
  "partner-10": "assets/partner-kinh-thien.jpg",
  "partner-11": "assets/partner-vinh-hung.png",
};

function renderMenuGallery() {
  menuGalleryGrid.innerHTML = Object.keys(menus).flatMap((tier) =>
    menuDayOrder.map((day) => {
      const slotId = `menu-${tier}-${day}`;
      return `
        <article class="menu-gallery-card">
          <div class="editable-frame menu-gallery-photo" data-image-slot="${slotId}" data-image-label="Ảnh ${menuTierLabels[tier]} - ${menuSampleLabels[day]}" data-image-mode="frame" data-menu-badge="${menuTierPrices[tier]}"></div>
          <div class="menu-gallery-card-body">
            <strong class="menu-gallery-price">${menuTierPrices[tier]}</strong>
            <button type="button" data-gallery-select data-tier="${tier}" data-day="${day}">Xem ảnh này ↗</button>
          </div>
        </article>`;
    }),
  ).join("");
}

function setMenuGalleryOpen(open) {
  if (open) {
    Object.keys(menuDefaultImages).forEach((slotId) => ensureDefaultMenuImage(slotId, menuGallery));
    imageRecords.forEach(applyImageRecord);
  }
  menuGallery.hidden = !open;
  menuGalleryToggle.setAttribute("aria-expanded", String(open));
  menuGalleryToggle.textContent = open ? "Ẩn thư viện hình ảnh" : "Xem toàn bộ hình ảnh";
  if (open) {
    menuGallery.scrollIntoView({ behavior: "smooth", block: "start" });
    menuGalleryClose.focus({ preventScroll: true });
  }
}

renderMenuGallery();
document.querySelectorAll(".menu-photo-frame, .menu-gallery-photo").forEach((element) => {
  if (menuDefaultImages[element.dataset.imageSlot]) return;
  const placeholder = document.createElement("span");
  placeholder.className = "menu-empty-placeholder";
  placeholder.textContent = "Ảnh thực đơn đang được cập nhật";
  element.append(placeholder);
});
function ensureDefaultMenuImage(slotId, root = document) {
  if (!menuDefaultImages[slotId]) return;
  root.querySelectorAll(`[data-image-slot="${slotId}"]`).forEach((element) => element.classList.add("has-default-image"));
}
function ensureDefaultMenuImagesForTier(tier, root = document) {
  menuDayOrder.forEach((day) => ensureDefaultMenuImage(`menu-${tier}-${day}`, root));
}
Object.keys(partnerDefaultImages).forEach((slotId) => {
  document.querySelectorAll(`[data-image-slot="${slotId}"]`).forEach((element) => element.classList.add("has-default-image"));
});
document.querySelectorAll("[data-menu-photo]").forEach((photo) => {
  const [tier, day] = photo.dataset.menuPhoto.split("-");
  photo.dataset.menuBadge = menuTierPrices[tier];
});
updateMenuDisplay();
menuGalleryToggle.addEventListener("click", () => setMenuGalleryOpen(menuGallery.hidden));
menuGalleryClose.addEventListener("click", () => {
  setMenuGalleryOpen(false);
  menuGalleryToggle.focus();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !menuGallery.hidden) {
    event.preventDefault();
    setMenuGalleryOpen(false);
    menuGalleryToggle.focus();
  }
});
menuGalleryGrid.addEventListener("click", (event) => {
  const button = event.target.closest("[data-gallery-select]");
  if (!button) return;
  const tierTab = menuTabs.find((tab) => tab.dataset.menu === button.dataset.tier);
  if (tierTab) activateMenu(tierTab);
  activateMenuDay(button.dataset.day);
  setMenuGalleryOpen(false);
  document.querySelector(".menu-image-board").scrollIntoView({ behavior: "smooth", block: "center" });
});

const partnerMarquee = document.querySelector(".partner-marquee");
const partnerMotionToggle = document.querySelector("#partner-motion-toggle");
const reducedMotionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");

function setPartnerMotionPaused(paused) {
  partnerMarquee.classList.toggle("paused", paused);
  partnerMotionToggle.setAttribute("aria-pressed", String(paused));
  partnerMotionToggle.innerHTML = paused
    ? '<i aria-hidden="true">▶</i> Tiếp tục'
    : '<i aria-hidden="true">Ⅱ</i> Tạm dừng';
}

setPartnerMotionPaused(reducedMotionPreference.matches);
partnerMotionToggle.addEventListener("click", () => {
  setPartnerMotionPaused(!partnerMarquee.classList.contains("paused"));
});
reducedMotionPreference.addEventListener?.("change", (event) => {
  if (event.matches) setPartnerMotionPaused(true);
});

const contactForm = document.querySelector("#contact-form");
const toast = document.querySelector("#toast");
const toastTitle = document.querySelector("#toast-title");
const toastMessage = document.querySelector("#toast-message");
const contactSubmitButton = contactForm.querySelector(".form-submit");
const contactSubmitLabel = contactSubmitButton.querySelector("span");
const formNote = document.querySelector("#form-note");
const serviceSelect = contactForm.elements.service;
const contactMessage = contactForm.elements.message;
let toastTimer;

function getContactRecipientEmail() {
  const configuredEmail = contactForm.dataset.recipientEmail?.trim();
  if (configuredEmail) return configuredEmail;

  try {
    const actionUrl = new URL(contactForm.getAttribute("action"), window.location.href);
    const actionParts = actionUrl.pathname.split("/").filter(Boolean);
    const recipient = actionParts[actionParts.length - 1];
    if (recipient && recipient !== "ajax") return decodeURIComponent(recipient);
  } catch (error) {
    return "quocbinhan975@gmail.com";
  }

  return "quocbinhan975@gmail.com";
}

function getContactAjaxEndpoint() {
  try {
    const actionUrl = new URL(contactForm.getAttribute("action"), window.location.href);
    const actionParts = actionUrl.pathname.split("/").filter(Boolean);
    if (actionParts[0] !== "ajax") actionParts.unshift("ajax");
    actionUrl.pathname = `/${actionParts.join("/")}`;
    return actionUrl.toString();
  } catch (error) {
    return `https://formsubmit.co/ajax/${getContactRecipientEmail()}`;
  }
}

menuQuote.addEventListener("click", () => {
  const translate = window.QBA_I18N?.translate || ((value) => value);
  const selection = translate(menus[currentMenuTier].code);
  serviceSelect.value = "Suất ăn trưa";
  const quoteLine = `${translate("Tôi muốn nhận báo giá thực đơn")} ${selection}.`;
  if (!contactMessage.value.includes(selection)) {
    contactMessage.value = contactMessage.value.trim()
      ? `${quoteLine}\n${contactMessage.value.trim()}`
      : quoteLine;
  }
  serviceSelect.closest("label").classList.add("field-highlight");
  contactMessage.closest("label").classList.add("field-highlight");
  setTimeout(() => {
    serviceSelect.closest("label").classList.remove("field-highlight");
    contactMessage.closest("label").classList.remove("field-highlight");
  }, 1800);
});

document.querySelectorAll("[data-service-interest]").forEach((link) => {
  link.addEventListener("click", () => {
    serviceSelect.value = link.dataset.serviceInterest;
    const label = serviceSelect.closest("label");
    label.classList.add("field-highlight");
    setTimeout(() => label.classList.remove("field-highlight"), 1800);
  });
});

function showContactToast(title, message, isError = false) {
  const translate = window.QBA_I18N?.translate || ((value) => value);
  toastTitle.textContent = translate(title);
  toastMessage.textContent = translate(message);
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 5200);
}

function buildMailto(formData) {
  const translate = window.QBA_I18N?.translate || ((value) => value);
  const recipientEmail = getContactRecipientEmail();
  const name = String(formData.get("name") || "").trim();
  const company = String(formData.get("company") || "").trim();
  const phone = String(formData.get("phone") || "").trim();
  const email = String(formData.get("email") || "").trim();
  const meals = String(formData.get("meals") || "").trim();
  const mealPrice = String(formData.get("meal_price") || "").trim();
  const service = String(formData.get("service") || "").trim();
  const region = String(formData.get("region") || "").trim();
  const message = String(formData.get("message") || "").trim();
  const subject = `${translate("Yêu cầu tư vấn suất ăn")} - ${company || name}`;
  const body = [
    translate("Kính gửi Công ty Quốc Bình An,"),
    "",
    translate("Tôi muốn được tư vấn dịch vụ suất ăn công nghiệp với thông tin:"),
    `${translate("Họ và tên")}: ${name}`,
    `${translate("Doanh nghiệp")}: ${company}`,
    `${translate("Số điện thoại")}: ${phone}`,
    `${translate("Email")}: ${email || translate("Không cung cấp")}`,
    `${translate("Số suất dự kiến mỗi ngày")}: ${meals || translate("Chưa xác định")}`,
    `${translate("Đơn giá suất ăn dự kiến")}: ${mealPrice || translate("Chưa xác định")}`,
    `${translate("Dịch vụ quan tâm")}: ${translate(service)}`,
    `${translate("Khu vực phục vụ")}: ${translate(region)}`,
    `${translate("Nhu cầu")}: ${message || translate("Tư vấn thêm qua điện thoại")}`,
    "",
    translate("Trân trọng."),
  ].join("\n");

  return `mailto:${recipientEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

function syncLocalPreviewFormNote() {
  if (window.location.protocol !== "file:") return;
  const translate = window.QBA_I18N?.translate || ((value) => value);
  formNote.textContent = translate("Bản xem trước trên máy sẽ mở ứng dụng email. Khi website được đăng tải, biểu mẫu sẽ tự gửi trực tiếp đến email công ty.");
}

syncLocalPreviewFormNote();
document.addEventListener("qba:languagechange", syncLocalPreviewFormNote);

contactForm.addEventListener("submit", (event) => {
  if (window.location.protocol !== "file:") return;

  event.preventDefault();
  const formData = new FormData(contactForm);
  showContactToast("Đang mở ứng dụng email…", "Nội dung đã được điền sẵn; hãy kiểm tra và bấm Gửi.");
  window.location.href = buildMailto(formData);
});

const hotlineModal = document.querySelector("#hotline-modal");
const hotlineCloseButton = hotlineModal.querySelector(".hotline-close");
let hotlineTrigger = null;

function openHotline(event) {
  event.preventDefault();
  hotlineTrigger = event.currentTarget;
  hotlineModal.hidden = false;
  hotlineModal.setAttribute("aria-hidden", "false");
  document.body.classList.add("hotline-open");
  requestAnimationFrame(() => {
    hotlineModal.classList.add("open");
    hotlineCloseButton.focus();
  });
}

function closeHotline() {
  if (hotlineModal.hidden) return;
  hotlineModal.classList.remove("open");
  hotlineModal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("hotline-open");
  setTimeout(() => {
    hotlineModal.hidden = true;
    hotlineTrigger?.focus();
  }, 260);
}

document.querySelectorAll("[data-hotline]").forEach((link) => link.addEventListener("click", openHotline));
hotlineModal.querySelectorAll("[data-hotline-close]").forEach((button) => button.addEventListener("click", closeHotline));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !hotlineModal.hidden) closeHotline();
  if (event.key !== "Tab" || hotlineModal.hidden) return;
  const focusable = [...hotlineModal.querySelectorAll('button:not([disabled]):not([tabindex="-1"]), a[href]')];
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
});

if (window.matchMedia("(pointer: fine)").matches) {
  cursorGlow.style.opacity = "1";
  window.addEventListener(
    "pointermove",
    (event) => {
      cursorGlow.style.left = `${event.clientX}px`;
      cursorGlow.style.top = `${event.clientY}px`;
    },
    { passive: true },
  );
}

const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
const heroSequence = document.querySelector(".hero-sequence");

if (heroSequence && !reducedMotionQuery.matches) {
  const heroImages = [...heroSequence.querySelectorAll("img")];
  const waitForHeroImages = Promise.all(
    heroImages.map((image) => {
      if (image.complete && image.naturalWidth > 0) return Promise.resolve();
      return new Promise((resolve) => {
        image.addEventListener("load", resolve, { once: true });
        image.addEventListener("error", resolve, { once: true });
      });
    }),
  );

  waitForHeroImages.then(() => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => heroSequence.classList.add("is-running"));
    });
  });
}

if (!reducedMotionQuery.matches) {
  const heroBackdrop = document.querySelector(".hero-backdrop");
  if (heroBackdrop && !heroBackdrop.querySelector(".hero-sequence")) {
    window.addEventListener(
      "scroll",
      () => {
        if (window.scrollY < window.innerHeight) {
          heroBackdrop.style.transform = `translateY(${window.scrollY * 0.08}px) scale(1.01)`;
        }
      },
      { passive: true },
    );
  }
}

// Trình quản lý hình ảnh cục bộ — ảnh chỉ được lưu trong IndexedDB của trình duyệt.
const IMAGE_DB_NAME = "qba-image-editor";
const IMAGE_DB_VERSION = 1;
const IMAGE_STORE_NAME = "images";
const IMAGE_MAX_BYTES = 10 * 1024 * 1024;
const IMAGE_MAX_EDGE = 1600;
const IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const HERO_DEFAULT_REVISION_KEY = "qba-hero-default-revision";
const HERO_DEFAULT_REVISION = "2026-07-12-food-processing";
const MENU_25K_SAMPLE_01_REVISION_KEY = "qba-menu-25k-sample-01-revision";
const MENU_25K_SAMPLE_01_REVISION = "2026-07-19-force-empty-25k";
const MENU_25K_IMAGE_REVISION_KEY = "qba-menu-25k-image-revision";
const MENU_25K_IMAGE_REVISION = "2026-07-31-replace-actual-samples-v1";
const MENU_24K_ACTUAL_IMAGES_REVISION_KEY = "qba-menu-24k-actual-images-revision";
const MENU_24K_ACTUAL_IMAGES_REVISION = "2026-07-25-separate-actual-samples-v2";
const MENU_23K_ACTUAL_IMAGES_REVISION_KEY = "qba-menu-23k-actual-images-revision";
const MENU_23K_ACTUAL_IMAGES_REVISION = "2026-08-03-actual-gallery-v1";
const MENU_23K_WEEK_IMAGES_REVISION_KEY = "qba-menu-23k-week-images-revision";
const MENU_23K_WEEK_IMAGES_REVISION = "2026-08-01-actual-samples-v1";
const MENU_EXPERT_WEEK_IMAGES_REVISION_KEY = "qba-menu-expert-week-images-revision";
const MENU_EXPERT_WEEK_IMAGES_REVISION = "2026-08-05-expert-v3-v1";
const MENU_EXPERT_ACTUAL_IMAGES_REVISION_KEY = "qba-menu-expert-actual-images-revision";
const MENU_EXPERT_ACTUAL_IMAGES_REVISION = "2026-08-05-separate-actual-samples-v1";
const MENU_PRICE_REMAP_REVISION_KEY = "qba-menu-price-remap-revision";
const MENU_PRICE_REMAP_REVISION = "2026-07-23-basic-week-v3-placeholders-v3";
const SERVICE_DEFAULT_IMAGES_REVISION_KEY = "qba-service-default-images-revision";
const SERVICE_DEFAULT_IMAGES_REVISION = "2026-08-09-restore-defaults-v1";
const SERVICE_IMAGE_SLOT_IDS = ["service-lunch", "service-event", "service-vegan", "service-breakfast", "service-night"];
const FRAME_LAYOUT_STORAGE_KEY = "qba-image-frame-layout-v1";
const FRAME_RESIZE_DIRECTIONS = ["n", "e", "s", "w", "ne", "nw", "se", "sw"];
const FRAME_RESIZE_LIMITS = { minWidth: 72, minHeight: 72, maxWidth: 1800, maxHeight: 1600 };
const imageSlotGroups = new Map();
const imageRecords = new Map();
const imageFrameRecords = new Map();
const registeredImageSlotElements = new WeakSet();
let activeImageSlotId = null;
let imageEditorToastTimer;

const imageEditorToggle = document.querySelector("#image-editor-toggle");
const imageManager = document.querySelector("#image-manager");
const imageManagerClose = document.querySelector("#image-manager-close");
const imageManagerList = document.querySelector("#image-manager-list");
const imageFileInput = document.querySelector("#image-file-input");
const imageConfigInput = document.querySelector("#image-config-input");
const imageEditorToast = document.querySelector("#image-editor-toast");
const draftEditorToggle = document.querySelector("#draft-editor-toggle");
const draftEditorPopover = document.querySelector("#draft-editor-popover");
const draftEditImages = document.querySelector("#draft-edit-images");
const draftEditContent = document.querySelector("#draft-edit-content");
const imageEditorAllowed = window.location.protocol === "file:" || new URLSearchParams(window.location.search).get("edit") === "1";
const PROFILE_PDF_PATH = "output/pdf/HSNL-Quoc-Binh-An-Catering-WEBSITE.pdf";
const PROFILE_PDF_MAX_BYTES = 80 * 1024 * 1024;
const PROFILE_PDF_EDITOR_PORTS = Array.from({ length: 10 }, (_, index) => 8791 + index);
const profilePdfCard = document.querySelector("[data-profile-pdf-dropzone]");
const profilePdfCover = document.querySelector(".profile-cover-frame");
const profilePdfLinks = [...document.querySelectorAll("[data-profile-pdf-link]")];
const profilePdfUpload = document.querySelector("[data-profile-pdf-upload]");
const profilePdfUploadLabel = document.querySelector("[data-profile-pdf-upload-label]");
const profilePdfInput = document.querySelector("#profile-pdf-input");
const profilePdfStatus = document.querySelector(".profile-pdf-status");
let profilePdfUploading = false;

document.body.classList.toggle("image-editor-available", imageEditorAllowed);
imageEditorToggle.hidden = !imageEditorAllowed;
draftEditorToggle.hidden = !imageEditorAllowed;

function translateProfilePdf(value) {
  return (window.QBA_I18N?.translate || ((text) => text))(value);
}

function isProfilePdfFile(file) {
  if (!file) return false;
  return file.type === "application/pdf" || /\.pdf$/i.test(file.name || "");
}

function isProfilePdfTransfer(dataTransfer) {
  return [...(dataTransfer?.items || [])].some((item) => item.kind === "file" && item.type === "application/pdf");
}

function setProfilePdfStatus(message = "", isError = false) {
  if (!profilePdfStatus) return;
  profilePdfStatus.textContent = message;
  profilePdfStatus.classList.toggle("error", isError);
  profilePdfStatus.hidden = !message;
}

function setProfilePdfUploadLabel(message) {
  if (profilePdfUploadLabel) profilePdfUploadLabel.textContent = message;
}

function setProfilePdfLink(path = PROFILE_PDF_PATH) {
  const separator = path.includes("?") ? "&" : "?";
  const href = `${path}${separator}v=${Date.now()}`;
  profilePdfLinks.forEach((link) => link.setAttribute("href", href));
}

async function probeProfilePdfEditorServer() {
  const probes = PROFILE_PDF_EDITOR_PORTS.map(async (port) => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 900);
    try {
      const origin = `http://127.0.0.1:${port}`;
      const response = await fetch(`${origin}/health`, { cache: "no-store", signal: controller.signal });
      if (!response.ok) return null;
      const payload = await response.json();
      return payload?.service === "hsnl-pdf-editor" ? origin : null;
    } catch (error) {
      return null;
    } finally {
      window.clearTimeout(timeout);
    }
  });
  const results = await Promise.all(probes);
  return results.find(Boolean) || "";
}

async function processProfilePdfFile(file) {
  if (!file || profilePdfUploading) return;
  if (!isProfilePdfFile(file)) {
    setProfilePdfStatus(translateProfilePdf("Chỉ hỗ trợ file PDF."), true);
    return;
  }
  if (file.size > PROFILE_PDF_MAX_BYTES) {
    setProfilePdfStatus(translateProfilePdf("PDF vượt quá dung lượng tối đa 80MB."), true);
    return;
  }

  profilePdfUploading = true;
  profilePdfCard?.classList.add("profile-pdf-uploading");
  if (profilePdfUpload) profilePdfUpload.disabled = true;
  setProfilePdfUploadLabel(translateProfilePdf("Đang lưu PDF…"));
  setProfilePdfStatus(translateProfilePdf("Đang lưu PDF…"));

  try {
    const editorOrigin = await probeProfilePdfEditorServer();
    if (!editorOrigin) {
      throw new Error("PROFILE_PDF_SERVER_NOT_FOUND");
    }
    const dataUrl = await readBlobAsDataUrl(file);
    const response = await fetch(`${editorOrigin}/api/profile-pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: file.name, mime: file.type, dataUrl }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "PROFILE_PDF_UPLOAD_FAILED");
    }
    setProfilePdfLink(payload.path || PROFILE_PDF_PATH);
    setProfilePdfStatus(translateProfilePdf("Đã cập nhật hồ sơ năng lực PDF."));
  } catch (error) {
    const message = error?.message === "PROFILE_PDF_SERVER_NOT_FOUND"
      ? "Không tìm thấy máy chủ chỉnh sửa HSNL. Hãy mở Mo-HSNL-Editor.command rồi thử lại."
      : "Không thể lưu PDF. Vui lòng thử lại.";
    setProfilePdfStatus(translateProfilePdf(message), true);
  } finally {
    profilePdfUploading = false;
    profilePdfCard?.classList.remove("profile-pdf-uploading", "profile-pdf-drag-over");
    if (profilePdfUpload) profilePdfUpload.disabled = false;
    setProfilePdfUploadLabel(translateProfilePdf("Chọn PDF"));
    if (profilePdfInput) profilePdfInput.value = "";
  }
}

function initializeProfilePdfControls() {
  profilePdfCover?.addEventListener("click", (event) => {
    if (document.body.classList.contains("image-edit-mode") || event.target.closest("a, button")) return;
    const link = profilePdfLinks[0];
    if (link?.href) window.open(link.href, "_blank", "noopener");
  });

  if (!profilePdfCard || !profilePdfInput || !profilePdfUpload) return;
  profilePdfUpload.hidden = !imageEditorAllowed;
  profilePdfUpload.addEventListener("click", () => profilePdfInput.click());
  profilePdfInput.addEventListener("change", () => processProfilePdfFile(profilePdfInput.files?.[0]));

  profilePdfCard.addEventListener("dragover", (event) => {
    if (!imageEditorAllowed || !isProfilePdfTransfer(event.dataTransfer)) return;
    event.preventDefault();
    event.stopPropagation();
    profilePdfCard.classList.add("profile-pdf-drag-over");
    setProfilePdfUploadLabel(translateProfilePdf("Thả PDF để cập nhật"));
  });

  profilePdfCard.addEventListener("dragleave", (event) => {
    if (!imageEditorAllowed || profilePdfCard.contains(event.relatedTarget)) return;
    profilePdfCard.classList.remove("profile-pdf-drag-over");
    setProfilePdfUploadLabel(translateProfilePdf("Chọn PDF"));
  });

  profilePdfCard.addEventListener("drop", (event) => {
    if (!imageEditorAllowed) return;
    const file = [...(event.dataTransfer?.files || [])].find(isProfilePdfFile);
    if (!file) return;
    event.preventDefault();
    event.stopPropagation();
    profilePdfCard.classList.remove("profile-pdf-drag-over");
    processProfilePdfFile(file);
  });

  document.addEventListener("qba:languagechange", () => {
    if (!profilePdfUploading) setProfilePdfUploadLabel(translateProfilePdf("Chọn PDF"));
    setProfilePdfStatus("");
  });
}

initializeProfilePdfControls();

function setDraftEditorPopover(open) {
  if (!draftEditorPopover || !draftEditorToggle) return;
  draftEditorPopover.classList.toggle("open", open);
  draftEditorPopover.setAttribute("aria-hidden", String(!open));
  draftEditorToggle.setAttribute("aria-expanded", String(open));
}

function closeDraftEditorPopover() {
  setDraftEditorPopover(false);
}

function syncDraftEditorControls() {
  const isEditing = document.body.classList.contains("image-edit-mode") || document.body.classList.contains("content-edit-mode");
  draftEditorToggle?.classList.toggle("active", isEditing);
}

function openImageDatabase() {
  return new Promise((resolve, reject) => {
    if (!window.indexedDB) {
      reject(new Error("Trình duyệt không hỗ trợ IndexedDB."));
      return;
    }

    const request = indexedDB.open(IMAGE_DB_NAME, IMAGE_DB_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains(IMAGE_STORE_NAME)) {
        database.createObjectStore(IMAGE_STORE_NAME, { keyPath: "id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function imageDbTransaction(mode, operation) {
  const database = await openImageDatabase();
  return new Promise((resolve, reject) => {
    const transaction = database.transaction(IMAGE_STORE_NAME, mode);
    const store = transaction.objectStore(IMAGE_STORE_NAME);
    const request = operation(store);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
    transaction.oncomplete = () => database.close();
    transaction.onerror = () => reject(transaction.error);
  });
}

const getAllImageRecords = () => imageDbTransaction("readonly", (store) => store.getAll());
const saveImageRecord = (record) => imageDbTransaction("readwrite", (store) => store.put(record));
const deleteImageRecord = (id) => imageDbTransaction("readwrite", (store) => store.delete(id));
const clearImageRecords = () => imageDbTransaction("readwrite", (store) => store.clear());

function canResizeImageSlot(slot) {
  return Boolean(slot && slot.mode !== "background" && slot.mode !== "logo");
}

function sanitizeFrameRecord(record) {
  if (!record?.id || !imageSlotGroups.has(record.id)) return null;
  const width = Math.max(FRAME_RESIZE_LIMITS.minWidth, Math.min(FRAME_RESIZE_LIMITS.maxWidth, Number(record.width) || 0));
  const height = Math.max(FRAME_RESIZE_LIMITS.minHeight, Math.min(FRAME_RESIZE_LIMITS.maxHeight, Number(record.height) || 0));
  return {
    id: record.id,
    width,
    height,
    marginLeft: Math.max(-800, Math.min(800, Number(record.marginLeft) || 0)),
    marginTop: Math.max(-800, Math.min(800, Number(record.marginTop) || 0)),
    updatedAt: record.updatedAt || new Date().toISOString(),
  };
}

function readStoredFrameRecords() {
  try {
    const payload = JSON.parse(localStorage.getItem(FRAME_LAYOUT_STORAGE_KEY) || "[]");
    return Array.isArray(payload) ? payload : [];
  } catch (error) {
    return [];
  }
}

function persistFrameRecords() {
  try {
    localStorage.setItem(FRAME_LAYOUT_STORAGE_KEY, JSON.stringify([...imageFrameRecords.values()]));
  } catch (error) {
    showImageEditorToast("Không thể lưu kích thước khung trên trình duyệt này.", true);
  }
}

function getFrameBaseline(slot) {
  const visibleElement = slot.elements.find((entry) => entry.offsetWidth > 0 && entry.offsetHeight > 0);
  const element = visibleElement || slot.elements[0];
  if (!element) return { width: 240, height: 180, marginLeft: 0, marginTop: 0 };
  const menuStack = !visibleElement && element.classList.contains("menu-photo-frame")
    ? element.closest(".menu-photo-stack")
    : null;
  const measureTarget = menuStack && menuStack.offsetWidth > 0 && menuStack.offsetHeight > 0 ? menuStack : element;
  const bounds = measureTarget.getBoundingClientRect();
  const style = getComputedStyle(element);
  return {
    width: Math.round(bounds.width || measureTarget.offsetWidth || 240),
    height: Math.round(bounds.height || measureTarget.offsetHeight || 180),
    marginLeft: parseFloat(style.marginLeft) || 0,
    marginTop: parseFloat(style.marginTop) || 0,
  };
}

function getFrameRecordOrBaseline(id) {
  const slot = imageSlotGroups.get(id);
  if (!slot) return null;
  return imageFrameRecords.get(id) || { id, ...getFrameBaseline(slot) };
}

function applyFrameRecord(record) {
  const normalized = sanitizeFrameRecord(record);
  if (!normalized) return;
  const slot = imageSlotGroups.get(normalized.id);
  if (!canResizeImageSlot(slot)) return;
  imageFrameRecords.set(normalized.id, normalized);
  slot.elements.forEach((element) => {
    element.classList.add("has-frame-layout");
    element.style.setProperty("--frame-width", `${normalized.width}px`);
    element.style.setProperty("--frame-height", `${normalized.height}px`);
    element.style.setProperty("--frame-margin-left", `${normalized.marginLeft}px`);
    element.style.setProperty("--frame-margin-top", `${normalized.marginTop}px`);
  });
  syncMenuPhotoState();
}

function clearFrameRecord(id) {
  const slot = imageSlotGroups.get(id);
  if (!slot) return;
  imageFrameRecords.delete(id);
  slot.elements.forEach((element) => {
    element.classList.remove("has-frame-layout");
    element.style.removeProperty("--frame-width");
    element.style.removeProperty("--frame-height");
    element.style.removeProperty("--frame-margin-left");
    element.style.removeProperty("--frame-margin-top");
  });
  persistFrameRecords();
  syncMenuPhotoState();
}

function createFrameResizeHandles(slot, element) {
  if (!canResizeImageSlot(slot) || element.dataset.frameResizable === "true") return;
  element.dataset.frameResizable = "true";
  const handleWrap = document.createElement("span");
  handleWrap.className = "frame-resize-handles";
  handleWrap.setAttribute("aria-hidden", "true");
  FRAME_RESIZE_DIRECTIONS.forEach((direction) => {
    const handle = document.createElement("button");
    handle.type = "button";
    handle.className = `frame-resize-handle frame-resize-${direction}`;
    handle.dataset.frameResize = direction;
    handle.setAttribute("aria-label", `Kéo chỉnh khung ${slot.label}`);
    handle.addEventListener("pointerdown", (event) => startFrameResize(event, element, slot.id, direction));
    handleWrap.append(handle);
  });
  element.append(handleWrap);
}

function startFrameResize(event, element, id, direction) {
  if (!document.body.classList.contains("image-edit-mode")) return;
  event.preventDefault();
  event.stopPropagation();
  focusImageManagerSlot(id);

  const slot = imageSlotGroups.get(id);
  const baseline = getFrameRecordOrBaseline(id) || { id, ...getFrameBaseline(slot) };
  const start = {
    x: event.clientX,
    y: event.clientY,
    width: baseline.width,
    height: baseline.height,
    marginLeft: baseline.marginLeft || 0,
    marginTop: baseline.marginTop || 0,
  };

  element.setPointerCapture?.(event.pointerId);
  element.classList.add("frame-resizing");

  const clampWidth = (value) => Math.max(FRAME_RESIZE_LIMITS.minWidth, Math.min(FRAME_RESIZE_LIMITS.maxWidth, value));
  const clampHeight = (value) => Math.max(FRAME_RESIZE_LIMITS.minHeight, Math.min(FRAME_RESIZE_LIMITS.maxHeight, value));

  const onMove = (moveEvent) => {
    const dx = moveEvent.clientX - start.x;
    const dy = moveEvent.clientY - start.y;
    let width = start.width;
    let height = start.height;
    let marginLeft = start.marginLeft;
    let marginTop = start.marginTop;

    if (direction.includes("e")) width = clampWidth(start.width + dx);
    if (direction.includes("s")) height = clampHeight(start.height + dy);
    if (direction.includes("w")) {
      width = clampWidth(start.width - dx);
      marginLeft = start.marginLeft + (start.width - width);
    }
    if (direction.includes("n")) {
      height = clampHeight(start.height - dy);
      marginTop = start.marginTop + (start.height - height);
    }

    applyFrameRecord({ id, width: Math.round(width), height: Math.round(height), marginLeft: Math.round(marginLeft), marginTop: Math.round(marginTop), updatedAt: new Date().toISOString() });
  };

  const finish = () => {
    element.classList.remove("frame-resizing");
    element.removeEventListener("pointermove", onMove);
    element.removeEventListener("pointerup", finish);
    element.removeEventListener("pointercancel", finish);
    persistFrameRecords();
    renderImageManager();
    showImageEditorToast("Đã lưu kích thước khung ảnh.");
  };

  element.addEventListener("pointermove", onMove);
  element.addEventListener("pointerup", finish);
  element.addEventListener("pointercancel", finish);
}

function showImageEditorToast(message, isError = false) {
  imageEditorToast.textContent = message;
  imageEditorToast.classList.toggle("error", isError);
  imageEditorToast.classList.add("show");
  clearTimeout(imageEditorToastTimer);
  imageEditorToastTimer = setTimeout(() => imageEditorToast.classList.remove("show"), 3600);
}

function readBlobAsDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });
}

function loadDataUrlImage(dataUrl) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("Không thể đọc ảnh này."));
    image.src = dataUrl;
  });
}

async function prepareImageFile(file) {
  if (!IMAGE_TYPES.has(file.type)) {
    throw new Error("Chỉ hỗ trợ ảnh JPG, PNG hoặc WebP.");
  }
  if (file.size > IMAGE_MAX_BYTES) {
    throw new Error("Ảnh vượt quá dung lượng tối đa 10MB.");
  }

  const originalDataUrl = await readBlobAsDataUrl(file);
  const sourceImage = await loadDataUrlImage(originalDataUrl);
  const largestEdge = Math.max(sourceImage.naturalWidth, sourceImage.naturalHeight);

  if (largestEdge <= IMAGE_MAX_EDGE) {
    return {
      dataUrl: originalDataUrl,
      width: sourceImage.naturalWidth,
      height: sourceImage.naturalHeight,
      type: file.type,
    };
  }

  const scale = IMAGE_MAX_EDGE / largestEdge;
  const width = Math.round(sourceImage.naturalWidth * scale);
  const height = Math.round(sourceImage.naturalHeight * scale);
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d", { alpha: file.type === "image/png" });
  if (!context) throw new Error("Trình duyệt không thể tối ưu ảnh này.");
  context.drawImage(sourceImage, 0, 0, width, height);
  const outputType = file.type === "image/png" ? "image/png" : file.type === "image/webp" ? "image/webp" : "image/jpeg";
  const compressedBlob = await new Promise((resolve) => canvas.toBlob(resolve, outputType, 0.84));
  if (!compressedBlob) throw new Error("Không thể nén ảnh. Vui lòng thử ảnh khác.");
  return {
    dataUrl: await readBlobAsDataUrl(compressedBlob),
    width,
    height,
    type: outputType,
  };
}

function getDefaultOverlay(id, mode) {
  if (mode !== "background") return 0;
  if (id === "hero-bg") return 0;
  if (id === "about-bg") return 76;
  if (id === "service-lunch") return 58;
  return 72;
}

function overlayColorForSlot(id) {
  return id === "about-bg" ? "248,244,234" : "23,59,53";
}

function normalizeImageSource(source) {
  if (!source) return "";
  const cleanSource = String(source).trim().replace(/^["']|["']$/g, "");
  try {
    const url = new URL(cleanSource, window.location.href);
    const pagePath = window.location.pathname || "/";
    const pageFolder = pagePath.slice(0, pagePath.lastIndexOf("/") + 1);
    if (url.origin === window.location.origin && url.pathname.startsWith(pageFolder)) {
      return decodeURIComponent(url.pathname.slice(pageFolder.length));
    }
  } catch (error) {
    // CSS can return relative paths, data URLs, or file URLs. Use the original value when parsing is not useful.
  }
  return cleanSource;
}

function extractLastBackgroundUrl(value) {
  const matches = [...String(value || "").matchAll(/url\((?:"([^"]+)"|'([^']+)'|([^)]*))\)/g)];
  if (!matches.length) return "";
  const match = matches[matches.length - 1];
  return normalizeImageSource(match[1] || match[2] || match[3] || "");
}

function getImageRecordTarget(id, element) {
  if (id === "hero-bg") return document.querySelector(".hero-backdrop") || element;
  return element;
}

function getDefaultImageSourceFromElement(id, element) {
  if (!element) return "";
  if (element.dataset.menuWeekDefaultImage) return normalizeImageSource(element.dataset.menuWeekDefaultImage);
  if (menuDefaultImages[id]) return normalizeImageSource(menuDefaultImages[id]);
  if (partnerDefaultImages[id]) return normalizeImageSource(partnerDefaultImages[id]);

  const target = getImageRecordTarget(id, element);
  const targetStyle = target ? getComputedStyle(target) : null;
  const menuWeekImage = getComputedStyle(element).getPropertyValue("--menu-week-image");
  return extractLastBackgroundUrl(menuWeekImage)
    || extractLastBackgroundUrl(element.style.backgroundImage)
    || extractLastBackgroundUrl(targetStyle?.backgroundImage)
    || "";
}

function getDefaultImageSourceForSlot(id) {
  const slot = imageSlotGroups.get(id);
  if (!slot) return "";
  for (const element of slot.elements) {
    const source = getDefaultImageSourceFromElement(id, element);
    if (source) return source;
  }
  return "";
}

function getDefaultImageRecord(id) {
  const slot = imageSlotGroups.get(id);
  if (!slot) return null;
  const source = getDefaultImageSourceForSlot(id);
  if (!source) return null;
  const element = slot.elements[0];
  const mode = element?.dataset.imageMode || slot.mode || "frame";
  return {
    id,
    label: slot.label,
    mode,
    fit: element?.dataset.imageFit || slot.fit || (mode === "logo" ? "contain" : "cover"),
    filename: source.split("/").pop() || "default-image",
    dataUrl: source,
    width: 0,
    height: 0,
    type: "image/default",
    positionX: 50,
    positionY: 50,
    zoom: 100,
    rotate: 0,
    overlay: getDefaultOverlay(id, mode),
    updatedAt: new Date().toISOString(),
  };
}

function getEditableImageRecord(id) {
  return imageRecords.get(id) || getDefaultImageRecord(id);
}

function ensureEditableImageRecord(id) {
  const existing = imageRecords.get(id);
  if (existing) return existing;
  const defaultRecord = getDefaultImageRecord(id);
  if (!defaultRecord) return null;
  imageRecords.set(id, defaultRecord);
  applyImageRecord(defaultRecord);
  return defaultRecord;
}

function imageSizeForRecord(record) {
  const configuredFit = imageSlotGroups.get(record.id)?.fit;
  if (configuredFit === "cover" && Number(record.zoom || 100) === 100) return "cover";
  if (record.mode === "logo" || ((record.fit === "contain" || configuredFit === "contain") && Number(record.zoom || 100) === 100)) return "contain";
  return Number(record.zoom || 100) === 100 ? "cover" : `${record.zoom}%`;
}

function ensureImageLayer(element) {
  let layer = element.querySelector(":scope > .slot-image-layer");
  if (!layer) {
    layer = document.createElement("span");
    layer.className = "slot-image-layer";
    layer.setAttribute("aria-hidden", "true");
    element.prepend(layer);
  }
  return layer;
}

function removeImageLayer(element) {
  element.querySelector(":scope > .slot-image-layer")?.remove();
}

function setUploadTriggerLabel(element, text) {
  const label = element.querySelector(":scope > .slot-upload-trigger .slot-label");
  if (label) label.textContent = text;
}

function updateUploadTriggerLabels(id, text) {
  imageSlotGroups.get(id)?.elements.forEach((element) => setUploadTriggerLabel(element, text));
}

function focusImageManagerSlot(id) {
  imageManagerList.querySelectorAll(".image-manager-item.is-active").forEach((item) => item.classList.remove("is-active"));
  const item = [...imageManagerList.querySelectorAll(".image-manager-item")].find((entry) => entry.dataset.managerSlot === id);
  if (!item) return;
  item.classList.add("is-active");
  item.scrollIntoView({ behavior: "smooth", block: "center" });
}

function applyImageRecord(record) {
  const slot = imageSlotGroups.get(record.id);
  if (!slot) return;
  imageRecords.set(record.id, record);

  slot.elements.forEach((element) => {
    element.classList.add("has-custom-image");
    if (record.id.startsWith("menu-week-")) element.closest(".menu-week-gallery-card")?.classList.remove("is-empty");
    const position = `${record.positionX ?? 50}% ${record.positionY ?? 50}%`;
    const size = imageSizeForRecord(record);

    if (record.mode === "background") {
      const target = getImageRecordTarget(record.id, element);
      if (!target) return;
      const overlay = Math.max(0, Math.min(80, Number(record.overlay || 0))) / 100;
      const color = overlayColorForSlot(record.id);
      target.style.backgroundImage = overlay > 0
        ? `linear-gradient(rgba(${color},${overlay}), rgba(${color},${overlay})), url("${record.dataUrl}")`
        : `url("${record.dataUrl}")`;
      target.style.backgroundPosition = position;
      target.style.backgroundSize = size;
      target.style.backgroundRepeat = "no-repeat";
    } else {
      const layer = ensureImageLayer(element);
      layer.style.backgroundImage = `url("${record.dataUrl}")`;
      layer.style.backgroundPosition = position;
      layer.style.backgroundSize = size;
      layer.style.backgroundRepeat = "no-repeat";
      layer.style.transform = `rotate(${Number(record.rotate || 0)}deg)`;
      element.style.backgroundImage = "none";
      element.style.backgroundPosition = position;
      element.style.backgroundSize = size;
      element.style.backgroundRepeat = "no-repeat";
    }
    setUploadTriggerLabel(element, record.mode === "background" ? "Thay ảnh nền" : "Thay ảnh · kéo để căn");
  });

  syncMenuPhotoState();
}

const deferredImageTargets = new WeakMap();
const imageLoadObserver = "IntersectionObserver" in window
  ? new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const id = deferredImageTargets.get(entry.target);
      const record = imageRecords.get(id);
      const slot = imageSlotGroups.get(id);
      if (record) applyImageRecord(record);
      slot?.elements.forEach((element) => imageLoadObserver.unobserve(element));
    });
  }, { rootMargin: "600px 0px" })
  : null;

function scheduleImageRecord(record) {
  const slot = imageSlotGroups.get(record.id);
  if (!slot || !imageLoadObserver) {
    applyImageRecord(record);
    return;
  }
  imageRecords.set(record.id, record);
  slot.elements.forEach((element) => {
    deferredImageTargets.set(element, record.id);
    imageLoadObserver.observe(element);
  });
}

function clearAppliedImage(id) {
  const slot = imageSlotGroups.get(id);
  if (!slot) return;

  slot.elements.forEach((element) => {
    element.classList.remove("has-custom-image");
    removeImageLayer(element);
    element.style.removeProperty("background-image");
    element.style.removeProperty("background-position");
    element.style.removeProperty("background-size");
    element.style.removeProperty("background-repeat");
    setUploadTriggerLabel(element, "Bấm hoặc thả ảnh");
    if (id.startsWith("menu-week-")) element.closest(".menu-week-gallery-card")?.classList.toggle("is-empty", !element.classList.contains("has-default-image"));
  });

  if (id === "hero-bg") {
    const heroBackdrop = document.querySelector(".hero-backdrop");
    heroBackdrop.style.removeProperty("background-image");
    heroBackdrop.style.removeProperty("background-position");
    heroBackdrop.style.removeProperty("background-size");
    heroBackdrop.style.removeProperty("background-repeat");
  }

  imageRecords.delete(id);
  syncMenuPhotoState();
}

function syncMenuPhotoState() {
  const stack = document.querySelector(".menu-photo-stack");
  if (!stack) return;
  const activePhoto = stack.querySelector(".menu-photo-frame.active");
  stack.classList.toggle("has-images", Boolean(activePhoto?.classList.contains("has-custom-image") || activePhoto?.classList.contains("has-default-image")));
}

function createUploadTrigger(slot, element) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "slot-upload-trigger";
  button.setAttribute("aria-label", `Chọn ảnh cho ${slot.label}`);
  button.innerHTML = `<span class="slot-camera" aria-hidden="true">▣</span><span class="slot-label">Bấm hoặc thả ảnh</span>`;
  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    openImagePicker(slot.id);
  });
  element.append(button);
}

function pruneImageSlotElements(slot) {
  if (!slot) return;
  slot.elements = slot.elements.filter((element) => element.isConnected);
}

function registerImageSlots(root = document) {
  const candidates = [
    ...(root.matches?.("[data-image-slot]") ? [root] : []),
    ...root.querySelectorAll("[data-image-slot]"),
  ];
  candidates.forEach((element) => {
    if (registeredImageSlotElements.has(element)) return;
    const id = element.dataset.imageSlot;
    const label = element.dataset.imageLabel || id;
    const mode = element.dataset.imageMode || "frame";
    const fit = element.dataset.imageFit || (mode === "logo" ? "contain" : "cover");
    if (mode !== "background") {
      if (!element.hasAttribute("role")) element.setAttribute("role", "img");
      element.dataset.i18nSourceAriaLabel = label;
      element.setAttribute("aria-label", (window.QBA_I18N?.translate || ((value) => value))(label));
    }
    if (!imageSlotGroups.has(id)) {
      imageSlotGroups.set(id, { id, label, mode, fit, elements: [] });
    }
    const slot = imageSlotGroups.get(id);
    pruneImageSlotElements(slot);
    if (!slot.elements.includes(element)) slot.elements.push(element);
    registeredImageSlotElements.add(element);
    element.classList.add("image-slot-target");
    createUploadTrigger(slot, element);
    createFrameResizeHandles(slot, element);
    if (getDefaultImageSourceFromElement(id, element)) {
      setUploadTriggerLabel(element, mode === "background" ? "Thay ảnh nền" : "Thay ảnh · kéo để căn");
    }

    element.addEventListener("dragover", (event) => {
      if (!document.body.classList.contains("image-edit-mode")) return;
      if (id === "company-profile-cover" && isProfilePdfTransfer(event.dataTransfer)) return;
      event.preventDefault();
      event.stopPropagation();
      element.classList.add("image-drag-over");
      const labelNode = element.querySelector(":scope > .slot-upload-trigger .slot-label");
      if (labelNode) labelNode.textContent = "Thả ảnh để sử dụng";
    });

    element.addEventListener("dragleave", (event) => {
      event.stopPropagation();
      if (element.contains(event.relatedTarget)) return;
      element.classList.remove("image-drag-over");
      setUploadTriggerLabel(element, getEditableImageRecord(id) ? "Thay ảnh · kéo để căn" : "Bấm hoặc thả ảnh");
    });

    element.addEventListener("drop", (event) => {
      if (!document.body.classList.contains("image-edit-mode")) return;
      const file = event.dataTransfer?.files?.[0];
      if (id === "company-profile-cover" && isProfilePdfFile(file)) return;
      event.preventDefault();
      event.stopPropagation();
      element.classList.remove("image-drag-over");
      if (file) processImageForSlot(id, file);
    });

    element.addEventListener("click", (event) => {
      if (!document.body.classList.contains("image-edit-mode")) return;
      if (event.target.closest("button, a")) return;
      event.preventDefault();
      event.stopPropagation();
      focusImageManagerSlot(id);
      if (!getEditableImageRecord(id)) {
        openImagePicker(id);
        return;
      }
      showImageEditorToast("Kéo ảnh trong khung hoặc chỉnh thông số bên bảng phải.");
    });

    if (mode !== "logo") enableImagePositionDragging(element, id);
  });
}

function enableImagePositionDragging(element, id) {
  let pointerState = null;
  element.addEventListener("pointerdown", (event) => {
    if (!document.body.classList.contains("image-edit-mode")) return;
    if (event.target.closest("button, a, input, textarea, select, [contenteditable], .slot-upload-trigger, .frame-resize-handle")) return;
    const record = getEditableImageRecord(id);
    if (!record) return;
    pointerState = {
      startX: event.clientX,
      startY: event.clientY,
      positionX: record.positionX ?? 50,
      positionY: record.positionY ?? 50,
      committed: false,
    };
    element.setPointerCapture?.(event.pointerId);
    event.preventDefault();
  });

  element.addEventListener("pointermove", (event) => {
    if (!pointerState) return;
    const dx = event.clientX - pointerState.startX;
    const dy = event.clientY - pointerState.startY;
    if (!pointerState.committed && Math.hypot(dx, dy) < 4) return;
    if (!pointerState.committed) {
      const editableRecord = ensureEditableImageRecord(id);
      if (!editableRecord) return;
      pointerState.committed = true;
      element.classList.add("image-positioning");
    }
    const record = imageRecords.get(id);
    if (!record) return;
    const bounds = element.getBoundingClientRect();
    record.positionX = Math.max(0, Math.min(100, pointerState.positionX + (dx / bounds.width) * 100));
    record.positionY = Math.max(0, Math.min(100, pointerState.positionY + (dy / bounds.height) * 100));
    applyImageRecord(record);
  });

  async function finishPositioning() {
    if (!pointerState) return;
    const shouldSave = pointerState.committed;
    pointerState = null;
    element.classList.remove("image-positioning");
    if (!shouldSave) return;
    try {
      const record = imageRecords.get(id);
      if (!record) return;
      await saveImageRecord(record);
      renderImageManager();
      showImageEditorToast("Đã lưu vị trí ảnh.");
    } catch (error) {
      showImageEditorToast("Không thể lưu vị trí ảnh.", true);
    }
  }

  element.addEventListener("pointerup", finishPositioning);
  element.addEventListener("pointercancel", finishPositioning);
}

function openImagePicker(id) {
  activeImageSlotId = id;
  imageFileInput.value = "";
  imageFileInput.click();
}

async function processImageForSlot(id, file) {
  const slot = imageSlotGroups.get(id);
  if (!slot) return;
  slot.elements.forEach((element) => element.classList.add("image-processing"));
  showImageEditorToast("Đang xử lý và tối ưu ảnh...");

  try {
    const prepared = await prepareImageFile(file);
    const previous = imageRecords.get(id);
    const record = {
      id,
      label: slot.label,
      mode: slot.mode,
      fit: previous?.fit ?? slot.fit,
      filename: file.name,
      dataUrl: prepared.dataUrl,
      width: prepared.width,
      height: prepared.height,
      type: prepared.type,
      positionX: previous?.positionX ?? 50,
      positionY: previous?.positionY ?? 50,
      zoom: previous?.zoom ?? 100,
      rotate: previous?.rotate ?? 0,
      overlay: previous?.overlay ?? getDefaultOverlay(id, slot.mode),
      updatedAt: new Date().toISOString(),
    };
    await saveImageRecord(record);
    applyImageRecord(record);
    if (id.startsWith("menu-week-")) updateMenuDisplay();
    renderImageManager();
    showImageEditorToast("Ảnh đã được lưu tự động trên trình duyệt.");
  } catch (error) {
    showImageEditorToast(error.message || "Không thể xử lý ảnh.", true);
  } finally {
    slot.elements.forEach((element) => element.classList.remove("image-processing", "image-drag-over"));
  }
}

async function removeImageForSlot(id) {
  try {
    await deleteImageRecord(id);
    clearAppliedImage(id);
    if (id.startsWith("menu-week-")) updateMenuDisplay();
    renderImageManager();
    showImageEditorToast("Đã khôi phục hình ảnh mặc định.");
  } catch (error) {
    showImageEditorToast("Không thể khôi phục ảnh lúc này.", true);
  }
}

function refreshImageSlotRegistry() {
  registerImageSlots();
  imageSlotGroups.forEach((slot, id) => {
    pruneImageSlotElements(slot);
    if (!slot.elements.length) imageSlotGroups.delete(id);
  });
}

function renderImageManager() {
  refreshImageSlotRegistry();
  imageManagerList.innerHTML = "";
  imageSlotGroups.forEach((slot) => {
    const record = imageRecords.get(slot.id);
    const defaultRecord = record ? null : getDefaultImageRecord(slot.id);
    const previewRecord = record || defaultRecord;
    const frameRecord = imageFrameRecords.get(slot.id);
    const frameState = canResizeImageSlot(slot) ? getFrameRecordOrBaseline(slot.id) : null;
    const item = document.createElement("article");
    item.className = "image-manager-item";
    item.dataset.managerSlot = slot.id;

    const thumb = document.createElement("div");
    thumb.className = "manager-thumb";
    if (previewRecord) {
      thumb.classList.add(record ? "has-saved-image" : "has-default-image");
      thumb.style.backgroundImage = `url("${previewRecord.dataUrl}")`;
      thumb.style.backgroundPosition = `${previewRecord.positionX ?? 50}% ${previewRecord.positionY ?? 50}%`;
      thumb.style.backgroundSize = previewRecord.mode === "logo" || slot.fit === "contain" || previewRecord.fit === "contain" ? "contain" : "cover";
    } else {
      thumb.textContent = "Chưa có ảnh";
    }

    const copy = document.createElement("div");
    copy.className = "manager-copy";
    const name = document.createElement("strong");
    name.textContent = slot.label;
    const status = document.createElement("span");
    status.className = `manager-status${record ? " saved" : ""}`;
    status.textContent = record
      ? (record.type === "image/default"
        ? (frameRecord ? "Đã lưu căn ảnh mặc định và kích thước khung" : "Đã lưu căn ảnh mặc định")
        : (frameRecord ? "Đã lưu ảnh và kích thước khung" : "Đã lưu tự động"))
      : (defaultRecord
        ? (frameRecord ? "Ảnh mặc định · đã chỉnh kích thước khung" : "Đang dùng ảnh mặc định")
        : (frameRecord ? "Đã chỉnh kích thước khung" : "Đang dùng giao diện mặc định"));
    const buttons = document.createElement("div");
    buttons.className = "manager-buttons";
    buttons.innerHTML = `
      <button type="button" data-image-action="replace" data-slot-id="${slot.id}">${previewRecord ? "Thay ảnh" : "Chọn ảnh"}</button>
      <button type="button" data-image-action="save" data-slot-id="${slot.id}">Lưu</button>
      <button type="button" class="danger" data-image-action="remove" data-slot-id="${slot.id}" ${record ? "" : "disabled"}>Khôi phục</button>
      ${canResizeImageSlot(slot) ? `<button type="button" data-image-action="reset-frame" data-slot-id="${slot.id}" ${frameRecord ? "" : "disabled"}>Khôi phục khung</button>` : ""}
    `;
    copy.append(name, status, buttons);
    item.append(thumb, copy);

    if (previewRecord || frameState) {
      const settings = document.createElement("div");
      settings.className = "manager-settings";
      const imageSettings = previewRecord ? `
        <label>Tâm ngang ${Math.round(previewRecord.positionX ?? 50)}%
          <input type="range" min="0" max="100" step="1" value="${previewRecord.positionX ?? 50}" data-setting="positionX" data-slot-id="${slot.id}" />
        </label>
        <label>Tâm dọc ${Math.round(previewRecord.positionY ?? 50)}%
          <input type="range" min="0" max="100" step="1" value="${previewRecord.positionY ?? 50}" data-setting="positionY" data-slot-id="${slot.id}" />
        </label>
        <label>Độ phóng ${previewRecord.zoom || 100}%
          <input type="range" min="${previewRecord.mode === "logo" ? "60" : "80"}" max="220" step="2" value="${previewRecord.zoom || 100}" data-setting="zoom" data-slot-id="${slot.id}" />
        </label>
        ${previewRecord.mode === "background" ? "" : `<label>Góc xoay ${previewRecord.rotate || 0}°<input type="range" min="-18" max="18" step="1" value="${previewRecord.rotate || 0}" data-setting="rotate" data-slot-id="${slot.id}" /></label>`}
        ${previewRecord.mode === "background" ? `<label>Lớp phủ ${previewRecord.overlay || 0}%<input type="range" min="0" max="80" step="5" value="${previewRecord.overlay || 0}" data-setting="overlay" data-slot-id="${slot.id}" /></label>` : ""}
        <label>Kéo ảnh trực tiếp<span>Bấm giữ trong khung để căn nhanh</span></label>` : "";
      const frameSettings = frameState ? `
        <label>Rộng khung ${Math.round(frameState.width)}px
          <input type="range" min="72" max="1400" step="4" value="${Math.round(frameState.width)}" data-frame-setting="width" data-slot-id="${slot.id}" />
        </label>
        <label>Cao khung ${Math.round(frameState.height)}px
          <input type="range" min="72" max="1200" step="4" value="${Math.round(frameState.height)}" data-frame-setting="height" data-slot-id="${slot.id}" />
        </label>
        <label>Lệch ngang ${Math.round(frameState.marginLeft || 0)}px
          <input type="range" min="-240" max="240" step="4" value="${Math.round(frameState.marginLeft || 0)}" data-frame-setting="marginLeft" data-slot-id="${slot.id}" />
        </label>
        <label>Lệch dọc ${Math.round(frameState.marginTop || 0)}px
          <input type="range" min="-240" max="240" step="4" value="${Math.round(frameState.marginTop || 0)}" data-frame-setting="marginTop" data-slot-id="${slot.id}" />
        </label>
        <label>Kéo khung trực tiếp<span>Kéo cạnh hoặc góc khung trên trang để đổi ngang/dọc.</span></label>` : "";
      settings.innerHTML = `${imageSettings}${frameSettings}`;
      item.append(settings);
    }

    imageManagerList.append(item);
  });
}

function setImageEditMode(enabled) {
  if (enabled && document.body.classList.contains("content-edit-mode")) setContentEditMode(false);
  closeDraftEditorPopover();
  document.body.classList.toggle("image-edit-mode", enabled);
  imageEditorToggle.classList.toggle("active", enabled);
  imageEditorToggle.setAttribute("aria-pressed", String(enabled));
  imageEditorToggle.querySelector(".editor-toggle-label").textContent = enabled ? "Đóng ảnh" : "Hình ảnh";
  imageManager.classList.toggle("open", enabled);
  imageManager.setAttribute("aria-hidden", String(!enabled));
  syncDraftEditorControls();
  if (enabled) {
    ensureDefaultMenuImagesForTier(currentMenuTier, menuPanel);
    imageRecords.forEach(applyImageRecord);
    renderImageManager();
    imageManagerClose.focus();
  }
}

draftEditorToggle?.addEventListener("click", (event) => {
  event.preventDefault();
  setDraftEditorPopover(!draftEditorPopover?.classList.contains("open"));
});

draftEditImages?.addEventListener("click", () => {
  setImageEditMode(true);
});

draftEditContent?.addEventListener("click", () => {
  setContentEditMode(true);
});

document.addEventListener("click", (event) => {
  if (!draftEditorPopover?.classList.contains("open")) return;
  if (event.target.closest("#site-editor-dock")) return;
  closeDraftEditorPopover();
});

imageEditorToggle.addEventListener("click", () => {
  setImageEditMode(!document.body.classList.contains("image-edit-mode"));
});

imageManagerClose.addEventListener("click", () => {
  setImageEditMode(false);
  imageEditorToggle.focus();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && draftEditorPopover?.classList.contains("open")) {
    closeDraftEditorPopover();
    draftEditorToggle?.focus();
    return;
  }
  if (event.key === "Escape" && hotlineModal.hidden && document.body.classList.contains("image-edit-mode")) {
    setImageEditMode(false);
    imageEditorToggle.focus();
  }
});

imageFileInput.addEventListener("change", () => {
  const file = imageFileInput.files?.[0];
  if (file && activeImageSlotId) processImageForSlot(activeImageSlotId, file);
});

imageManagerList.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-image-action]");
  if (!button) return;
  const id = button.dataset.slotId;
  const action = button.dataset.imageAction;
  if (action === "replace") openImagePicker(id);
  if (action === "remove" && imageRecords.has(id)) await removeImageForSlot(id);
  if (action === "reset-frame" && imageFrameRecords.has(id)) {
    clearFrameRecord(id);
    renderImageManager();
    showImageEditorToast("Đã khôi phục kích thước khung.");
  }
  if (action === "save") showImageEditorToast(imageRecords.has(id) || imageFrameRecords.has(id) ? "Dữ liệu đã được lưu tự động." : "Hãy chọn ảnh hoặc kéo chỉnh khung trước khi lưu.", !(imageRecords.has(id) || imageFrameRecords.has(id)));
});

function updateImageSetting(control) {
  const record = ensureEditableImageRecord(control.dataset.slotId);
  if (!record) return null;
  const value = Number(control.value);
  if (control.dataset.setting === "positionX") record.positionX = value;
  if (control.dataset.setting === "positionY") record.positionY = value;
  if (control.dataset.setting === "zoom") record.zoom = value;
  if (control.dataset.setting === "rotate") record.rotate = value;
  if (control.dataset.setting === "overlay") record.overlay = value;
  applyImageRecord(record);
  const label = control.closest("label");
  if (control.dataset.setting === "positionX") label.childNodes[0].textContent = `Tâm ngang ${Math.round(value)}%`;
  if (control.dataset.setting === "positionY") label.childNodes[0].textContent = `Tâm dọc ${Math.round(value)}%`;
  if (control.dataset.setting === "zoom") label.childNodes[0].textContent = `Độ phóng ${value}%`;
  if (control.dataset.setting === "rotate") label.childNodes[0].textContent = `Góc xoay ${value}°`;
  if (control.dataset.setting === "overlay") label.childNodes[0].textContent = `Lớp phủ ${value}%`;
  return record;
}

function updateFrameSetting(control) {
  const id = control.dataset.slotId;
  const slot = imageSlotGroups.get(id);
  if (!slot || !canResizeImageSlot(slot)) return null;
  const baseline = getFrameRecordOrBaseline(id);
  const value = Number(control.value);
  const record = {
    id,
    width: control.dataset.frameSetting === "width" ? value : baseline.width,
    height: control.dataset.frameSetting === "height" ? value : baseline.height,
    marginLeft: control.dataset.frameSetting === "marginLeft" ? value : baseline.marginLeft,
    marginTop: control.dataset.frameSetting === "marginTop" ? value : baseline.marginTop,
    updatedAt: new Date().toISOString(),
  };
  applyFrameRecord(record);
  const label = control.closest("label");
  if (control.dataset.frameSetting === "width") label.childNodes[0].textContent = `Rộng khung ${Math.round(value)}px`;
  if (control.dataset.frameSetting === "height") label.childNodes[0].textContent = `Cao khung ${Math.round(value)}px`;
  if (control.dataset.frameSetting === "marginLeft") label.childNodes[0].textContent = `Lệch ngang ${Math.round(value)}px`;
  if (control.dataset.frameSetting === "marginTop") label.childNodes[0].textContent = `Lệch dọc ${Math.round(value)}px`;
  return imageFrameRecords.get(id);
}

imageManagerList.addEventListener("input", (event) => {
  const control = event.target.closest("[data-setting]");
  const frameControl = event.target.closest("[data-frame-setting]");
  if (control) updateImageSetting(control);
  if (frameControl) updateFrameSetting(frameControl);
});

imageManagerList.addEventListener("change", async (event) => {
  const control = event.target.closest("[data-setting]");
  const frameControl = event.target.closest("[data-frame-setting]");
  if (control) {
    const record = updateImageSetting(control);
    if (!record) return;
    try {
      await saveImageRecord(record);
      showImageEditorToast("Đã lưu điều chỉnh ảnh.");
    } catch (error) {
      showImageEditorToast("Không thể lưu điều chỉnh ảnh.", true);
    }
  }
  if (frameControl) {
    const frameRecord = updateFrameSetting(frameControl);
    if (!frameRecord) return;
    persistFrameRecords();
    renderImageManager();
    showImageEditorToast("Đã lưu kích thước khung.");
  }
});

document.querySelector("#image-export").addEventListener("click", async () => {
  try {
    const records = [...imageRecords.values()];
    const frameRecords = [...imageFrameRecords.values()];
    const payload = JSON.stringify({ version: 2, exportedAt: new Date().toISOString(), records, frameRecords }, null, 2);
    const blob = new Blob([payload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "image-config.json";
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
    showImageEditorToast("Đã xuất image-config.json để đưa lên hosting.");
  } catch (error) {
    showImageEditorToast("Không thể xuất dữ liệu hình ảnh.", true);
  }
});

document.querySelector("#image-import").addEventListener("click", () => {
  imageConfigInput.value = "";
  imageConfigInput.click();
});

imageConfigInput.addEventListener("change", async () => {
  const file = imageConfigInput.files?.[0];
  if (!file) return;
  try {
    const payload = JSON.parse(await file.text());
    if (!Array.isArray(payload.records)) throw new Error("Tệp dữ liệu không hợp lệ.");
    for (const record of payload.records) {
      if (!imageSlotGroups.has(record.id) || !record.dataUrl) continue;
      await saveImageRecord(record);
      applyImageRecord(record);
    }
    if (Array.isArray(payload.frameRecords)) {
      payload.frameRecords.forEach((frameRecord) => {
        const normalized = sanitizeFrameRecord(frameRecord);
        if (normalized && canResizeImageSlot(imageSlotGroups.get(normalized.id))) applyFrameRecord(normalized);
      });
      persistFrameRecords();
    }
    renderImageManager();
    showImageEditorToast("Đã nhập và khôi phục dữ liệu hình ảnh.");
  } catch (error) {
    showImageEditorToast(error.message || "Không thể nhập dữ liệu ảnh.", true);
  }
});

document.querySelector("#image-reset-all").addEventListener("click", async () => {
  if (!window.confirm("Khôi phục toàn bộ hình ảnh mặc định?")) return;
  try {
    await clearImageRecords();
    [...imageRecords.keys()].forEach(clearAppliedImage);
    [...imageFrameRecords.keys()].forEach((id) => {
      const slot = imageSlotGroups.get(id);
      imageFrameRecords.delete(id);
      slot?.elements.forEach((element) => {
        element.classList.remove("has-frame-layout");
        element.style.removeProperty("--frame-width");
        element.style.removeProperty("--frame-height");
        element.style.removeProperty("--frame-margin-left");
        element.style.removeProperty("--frame-margin-top");
      });
    });
    persistFrameRecords();
    renderImageManager();
    showImageEditorToast("Đã khôi phục toàn bộ hình ảnh mặc định.");
  } catch (error) {
    showImageEditorToast("Không thể khôi phục ảnh lúc này.", true);
  }
});

async function initializeImageEditor() {
  registerImageSlots();
  const mergedRecords = new Map();
  const productionImageRecords = new Map();
  const mergedFrameRecords = new Map();
  const legacyMenuSlots = {
    "menu-standard": "menu-standard-mon",
    "menu-energy": "menu-energy-mon",
    "menu-premium": "menu-premium-mon",
    "menu-light": "menu-light-mon",
  };
  const mergeFrameRecord = (record) => {
    const targetId = legacyMenuSlots[record?.id] || record?.id;
    const normalized = sanitizeFrameRecord({ ...record, id: targetId });
    if (normalized && canResizeImageSlot(imageSlotGroups.get(normalized.id))) mergedFrameRecords.set(normalized.id, normalized);
  };

  const productionDraft = window.QBA_DRAFT_FINAL;
  if (Array.isArray(productionDraft?.imageRecords)) {
    productionDraft.imageRecords.forEach((record) => {
      const targetId = legacyMenuSlots[record.id] || record.id;
      if (!imageSlotGroups.has(targetId) || !record.dataUrl) return;
      const slot = imageSlotGroups.get(targetId);
      const productionRecord = { ...record, id: targetId, label: slot.label, mode: slot.mode, fit: slot.fit };
      productionImageRecords.set(targetId, productionRecord);
      mergedRecords.set(targetId, productionRecord);
    });
  }
  if (Array.isArray(productionDraft?.frameRecords)) productionDraft.frameRecords.forEach(mergeFrameRecord);

  if (window.location.protocol !== "file:") {
    try {
      const response = await fetch("image-config.json", { cache: "no-store" });
      if (response.ok) {
        const payload = await response.json();
        if (Array.isArray(payload.records)) {
          payload.records.forEach((record) => {
            const targetId = legacyMenuSlots[record.id] || record.id;
            if (imageSlotGroups.has(targetId) && record.dataUrl) {
              const slot = imageSlotGroups.get(targetId);
              mergedRecords.set(targetId, { ...record, id: targetId, label: slot.label, mode: slot.mode, fit: slot.fit });
            }
          });
        }
        if (Array.isArray(payload.frameRecords)) payload.frameRecords.forEach(mergeFrameRecord);
      }
    } catch (error) {
      // Tệp xuất bản ảnh là tùy chọn; giao diện mặc định vẫn hoạt động nếu chưa có.
    }
  }

  if (imageEditorAllowed) readStoredFrameRecords().forEach(mergeFrameRecord);

  try {
    let shouldResetStoredHero = false;
    let shouldResetMenu25kSample01 = false;
    let shouldResetMenu25kImages = false;
    let shouldResetMenu24kActualImages = false;
    let shouldResetMenu23kActualImages = false;
    let shouldResetMenu23kWeekImages = false;
    let shouldResetMenuExpertWeekImages = false;
    let shouldResetMenuExpertActualImages = false;
    let shouldResetMenuPriceRemapImages = false;
    let shouldResetServiceImages = false;
    if (imageEditorAllowed) {
      shouldResetStoredHero = localStorage.getItem(HERO_DEFAULT_REVISION_KEY) !== HERO_DEFAULT_REVISION;
      if (shouldResetStoredHero) {
        try {
          await deleteImageRecord("hero-bg");
        } catch (error) {
          // Nếu trình duyệt chặn bộ nhớ cục bộ, ảnh bếp mặc định trong HTML/CSS vẫn là lớp dự phòng.
        }
        localStorage.setItem(HERO_DEFAULT_REVISION_KEY, HERO_DEFAULT_REVISION);
      }
      shouldResetMenu25kImages = localStorage.getItem(MENU_25K_IMAGE_REVISION_KEY) !== MENU_25K_IMAGE_REVISION;
      if (shouldResetMenu25kImages) {
        try {
          await Promise.all(menuDayOrder.map((day) => deleteImageRecord(`menu-energy-${day}`)));
        } catch (error) {
          // Nếu bộ nhớ cục bộ không mở được, ảnh mặc định trong CSS vẫn là nguồn hiển thị chính.
        }
        localStorage.setItem(MENU_25K_IMAGE_REVISION_KEY, MENU_25K_IMAGE_REVISION);
      }
      shouldResetMenu25kSample01 = localStorage.getItem(MENU_25K_SAMPLE_01_REVISION_KEY) !== MENU_25K_SAMPLE_01_REVISION;
      if (shouldResetMenu25kSample01 && !shouldResetMenu25kImages) {
        try {
          await deleteImageRecord("menu-energy-mon");
        } catch (error) {
          // Nếu bộ nhớ cục bộ không mở được, ảnh mặc định trong CSS vẫn là nguồn hiển thị chính.
        }
        localStorage.setItem(MENU_25K_SAMPLE_01_REVISION_KEY, MENU_25K_SAMPLE_01_REVISION);
      }
      shouldResetMenu24kActualImages = localStorage.getItem(MENU_24K_ACTUAL_IMAGES_REVISION_KEY) !== MENU_24K_ACTUAL_IMAGES_REVISION;
      if (shouldResetMenu24kActualImages) {
        try {
          await Promise.all(menuDayOrder.map((day) => deleteImageRecord(`menu-standard-${day}`)));
        } catch (error) {
          // Chỉ khôi phục ảnh tách riêng 24K; ảnh lịch 24K vẫn dùng nhóm menu-week-standard-*.
        }
        menuDayOrder.forEach((day) => mergedRecords.delete(`menu-standard-${day}`));
        localStorage.setItem(MENU_24K_ACTUAL_IMAGES_REVISION_KEY, MENU_24K_ACTUAL_IMAGES_REVISION);
      }
      shouldResetMenu23kActualImages = localStorage.getItem(MENU_23K_ACTUAL_IMAGES_REVISION_KEY) !== MENU_23K_ACTUAL_IMAGES_REVISION;
      if (shouldResetMenu23kActualImages) {
        try {
          await Promise.all(menuDayOrder.map((day) => deleteImageRecord(`menu-basic-${day}`)));
        } catch (error) {
          // Chỉ khôi phục sáu ảnh thực tế tách riêng 23K; ảnh lịch 23K vẫn được giữ nguyên.
        }
        menuDayOrder.forEach((day) => mergedRecords.delete(`menu-basic-${day}`));
        localStorage.setItem(MENU_23K_ACTUAL_IMAGES_REVISION_KEY, MENU_23K_ACTUAL_IMAGES_REVISION);
      }
      shouldResetMenu23kWeekImages = localStorage.getItem(MENU_23K_WEEK_IMAGES_REVISION_KEY) !== MENU_23K_WEEK_IMAGES_REVISION;
      if (shouldResetMenu23kWeekImages) {
        try {
          await Promise.all(menuDayOrder.map((day) => deleteImageRecord(`menu-week-basic-${day}`)));
        } catch (error) {
          // Chỉ khôi phục sáu ảnh lịch 23K; các nhóm ảnh khác được giữ nguyên.
        }
        localStorage.setItem(MENU_23K_WEEK_IMAGES_REVISION_KEY, MENU_23K_WEEK_IMAGES_REVISION);
      }
      shouldResetMenuExpertWeekImages = localStorage.getItem(MENU_EXPERT_WEEK_IMAGES_REVISION_KEY) !== MENU_EXPERT_WEEK_IMAGES_REVISION;
      if (shouldResetMenuExpertWeekImages) {
        try {
          await Promise.all(menuDayOrder.map((day) => deleteImageRecord(`menu-week-light-${day}`)));
        } catch (error) {
          // Chỉ khôi phục sáu ảnh suất chuyên gia theo đúng thứ; các nhóm ảnh khác được giữ nguyên.
        }
        menuDayOrder.forEach((day) => mergedRecords.delete(`menu-week-light-${day}`));
        localStorage.setItem(MENU_EXPERT_WEEK_IMAGES_REVISION_KEY, MENU_EXPERT_WEEK_IMAGES_REVISION);
      }
      shouldResetMenuExpertActualImages = localStorage.getItem(MENU_EXPERT_ACTUAL_IMAGES_REVISION_KEY) !== MENU_EXPERT_ACTUAL_IMAGES_REVISION;
      if (shouldResetMenuExpertActualImages) {
        try {
          await Promise.all(menuDayOrder.map((day) => deleteImageRecord(`menu-light-${day}`)));
        } catch (error) {
          // Chỉ khôi phục sáu ảnh thực tế tách riêng của suất chuyên gia; ảnh lịch V3 vẫn được giữ nguyên.
        }
        menuDayOrder.forEach((day) => mergedRecords.delete(`menu-light-${day}`));
        localStorage.setItem(MENU_EXPERT_ACTUAL_IMAGES_REVISION_KEY, MENU_EXPERT_ACTUAL_IMAGES_REVISION);
      }
      shouldResetMenuPriceRemapImages = localStorage.getItem(MENU_PRICE_REMAP_REVISION_KEY) !== MENU_PRICE_REMAP_REVISION;
      if (shouldResetMenuPriceRemapImages) {
        try {
          await Promise.all(menuDayOrder.flatMap((day) => [
            deleteImageRecord(`menu-basic-${day}`),
            deleteImageRecord(`menu-energy-${day}`),
          ]));
        } catch (error) {
          // Nếu bộ nhớ cục bộ không mở được, ảnh mặc định trong CSS vẫn là nguồn hiển thị chính.
        }
        localStorage.setItem(MENU_PRICE_REMAP_REVISION_KEY, MENU_PRICE_REMAP_REVISION);
      }
      shouldResetServiceImages = localStorage.getItem(SERVICE_DEFAULT_IMAGES_REVISION_KEY) !== SERVICE_DEFAULT_IMAGES_REVISION;
      if (shouldResetServiceImages) {
        try {
          await Promise.all(SERVICE_IMAGE_SLOT_IDS.map((id) => deleteImageRecord(id)));
        } catch (error) {
          // Chỉ khôi phục năm ảnh dịch vụ mặc định; các khung ảnh khác được giữ nguyên.
        }
        SERVICE_IMAGE_SLOT_IDS.forEach((id) => mergedRecords.delete(id));
        localStorage.setItem(SERVICE_DEFAULT_IMAGES_REVISION_KEY, SERVICE_DEFAULT_IMAGES_REVISION);
      }
    }
    const records = await getAllImageRecords();
    if (imageEditorAllowed) {
      for (const record of records) {
        if (shouldResetStoredHero && record.id === "hero-bg") continue;
        if (shouldResetMenuPriceRemapImages && (record.id?.startsWith("menu-basic-") || record.id?.startsWith("menu-energy-"))) continue;
        if (shouldResetMenu24kActualImages && record.id?.startsWith("menu-standard-")) continue;
        if (shouldResetMenu23kActualImages && record.id?.startsWith("menu-basic-")) continue;
        if (shouldResetMenu23kWeekImages && record.id?.startsWith("menu-week-basic-")) continue;
        if (shouldResetMenuExpertWeekImages && record.id?.startsWith("menu-week-light-")) continue;
        if (shouldResetMenuExpertActualImages && record.id?.startsWith("menu-light-")) continue;
        if (shouldResetMenu25kImages && record.id?.startsWith("menu-energy-")) continue;
        if (shouldResetMenu25kSample01 && record.id === "menu-energy-mon") continue;
        if (shouldResetServiceImages && SERVICE_IMAGE_SLOT_IDS.includes(record.id)) continue;
        const migratedId = legacyMenuSlots[record.id];
        if (migratedId && imageSlotGroups.has(migratedId)) {
          const slot = imageSlotGroups.get(migratedId);
          const migratedRecord = { ...record, id: migratedId, label: slot.label, mode: slot.mode, fit: slot.fit };
          await saveImageRecord(migratedRecord);
          mergedRecords.set(migratedId, migratedRecord);
        } else if (imageSlotGroups.has(record.id)) {
          mergedRecords.set(record.id, record);
        }
      }
    }
  } catch (error) {
    if (imageEditorAllowed) showImageEditorToast("Không thể mở bộ nhớ ảnh cục bộ trên trình duyệt này.", true);
  }
  productionImageRecords.forEach((record, id) => {
    if (!mergedRecords.has(id)) mergedRecords.set(id, record);
  });
  mergedFrameRecords.forEach(applyFrameRecord);
  mergedRecords.forEach(scheduleImageRecord);
  window.__qbaImageEditorReady = true;
  updateMenuDisplay();
  renderImageManager();
}

initializeImageEditor();

// Trình chỉnh sửa nội dung trực tiếp — chữ và số được lưu tự động trên trình duyệt.
const ABOUT_CONTENT_REVISION_KEY = "qba-about-content-revision";
const ABOUT_CONTENT_REVISION = "2026-08-13-capacity-15k-final-v6";
const LOCATION_CONTENT_REVISION_KEY = "qba-location-content-revision";
const LOCATION_CONTENT_REVISION = "2026-07-24-representative-area-v2";
const MENU_CONTENT_REVISION_KEY = "qba-menu-content-revision";
const MENU_CONTENT_REVISION = "2026-07-23-lunch-only-editable";
const MENU_23K_CONTENT_REVISION_KEY = "qba-menu-23k-content-revision";
const MENU_23K_CONTENT_REVISION = "2026-08-01-actual-samples-v1";
const QUALITY_PROCESS_CONTENT_REVISION_KEY = "qba-quality-process-content-revision";
const QUALITY_PROCESS_CONTENT_REVISION = "2026-07-07-v1";
const CONTENT_HELP_TEXT = "Bấm trực tiếp vào chữ hoặc số · Tự động lưu";
const contentEditorToggle = document.querySelector("#content-editor-toggle");
const contentEditorBar = document.querySelector("#content-editor-bar");
const contentEditorDone = document.querySelector("#content-editor-done");
const contentResetSelected = document.querySelector("#content-reset-selected");
const contentResetAll = document.querySelector("#content-reset-all");
const contentEditorStatus = document.querySelector("#content-editor-status");
const contentGroups = new Map();
const contentOriginals = new Map();
let contentRecords = {};
let selectedContentTarget = null;
let contentSaveTimer = null;
let contentStatusTimer = null;

contentEditorToggle.hidden = !imageEditorAllowed;

const contentTargetSelector = [
  ".eyebrow",
  "#hero-title",
  ".hero-lead",
  ".hero-proof p",
  ".intro-strip > div > span",
  ".intro-strip > div > strong",
  "main .section-kicker",
  "main section h2",
  "main section h3",
  "main section h4",
  "main section p",
  ".panel-topline > span",
  ".meal-core",
  ".meal-preview > div:last-child > small",
  ".meal-preview > div:last-child > strong",
  ".meal-preview > div:last-child > span",
  ".panel-metrics span",
  ".panel-metrics strong",
  ".kitchen-promise span",
  ".company-profile-copy > span",
  ".company-profile-meta b",
  ".origin-note > span",
  ".origin-story article > strong",
  ".origin-story article > span",
  ".value-card > span",
  ".service-tag",
  ".menu-tab",
  ".process-step > span",
  ".stat-label",
  ".count",
  ".experience-placeholder",
  ".stat-card sup",
  ".coverage-pills span",
  ".map-note span",
  ".province-label strong",
  ".province-label small",
  ".map-caption span",
  ".map-caption strong",
  ".partner-marquee-toolbar > span",
  ".partner-logo > span",
  ".industry-list > span",
  ".industry-list > div",
  ".contact-info a > small",
  ".contact-info a > strong",
  ".contact-info a > span",
  ".footer-brand p",
  ".footer-privacy p",
].join(",");

function sanitizeContentHtml(html) {
  const template = document.createElement("template");
  template.innerHTML = html;
  const allowed = new Set(["BR", "SPAN", "STRONG", "SMALL", "SUP", "EM", "B", "I"]);
  [...template.content.querySelectorAll("*")].forEach((node) => {
    if (["SCRIPT", "STYLE", "IFRAME", "OBJECT", "EMBED", "FORM", "INPUT", "BUTTON"].includes(node.tagName)) {
      node.remove();
      return;
    }
    if (!allowed.has(node.tagName)) {
      node.replaceWith(...node.childNodes);
      return;
    }
    [...node.attributes].forEach((attribute) => node.removeAttribute(attribute.name));
  });
  return template.innerHTML.trim();
}

function getContentStorage() {
  try {
    const parsed = JSON.parse(localStorage.getItem(CONTENT_STORAGE_KEY) || "{}");
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (error) {
    return {};
  }
}

function persistContentStorage() {
  try {
    localStorage.setItem(CONTENT_STORAGE_KEY, JSON.stringify(contentRecords));
    return true;
  } catch (error) {
    setContentEditorStatus("Không thể lưu trên trình duyệt này", true);
    return false;
  }
}

function migrateAboutContent() {
  try {
    if (localStorage.getItem(ABOUT_CONTENT_REVISION_KEY) === ABOUT_CONTENT_REVISION) return;
    const capacityReplacements = [
      [/10\.000/g, "15.000"],
      [/10,000/g, "15,000"],
      [/\b10000\b/g, "15000"],
    ];
    let changed = false;
    Object.keys(contentRecords).forEach((key) => {
      if (!key.startsWith("about-") && !key.startsWith("capacity-")) return;
      const record = contentRecords[key];
      if (!record || typeof record.html !== "string") return;
      let migratedHtml = record.html;
      capacityReplacements.forEach(([pattern, replacement]) => {
        migratedHtml = migratedHtml.replace(pattern, replacement);
      });
      if (migratedHtml !== record.html) {
        record.html = migratedHtml;
        if (record.count === 10000) record.count = 15000;
        changed = true;
      }
    });
    if (changed) persistContentStorage();
    localStorage.setItem(ABOUT_CONTENT_REVISION_KEY, ABOUT_CONTENT_REVISION);
  } catch (error) {
    // Nội dung mặc định trong HTML vẫn được sử dụng khi bộ nhớ trình duyệt bị chặn.
  }
}

function migrateLocationContent() {
  try {
    if (localStorage.getItem(LOCATION_CONTENT_REVISION_KEY) === LOCATION_CONTENT_REVISION) return;
    const exactReplacements = new Map([
      ["Tiền Giang", "Đồng Tháp"],
      ["Đồng Nai", "TP. Đồng Nai"],
    ]);
    const replacements = [
      ["Bà Rịa – Vũng Tàu", "TP. Hồ Chí Minh"],
      ["Bà Rịa - Vũng Tàu", "TP. Hồ Chí Minh"],
      ["Khu vực đại diện: Biên Hòa", "Khu vực đại diện: Nhơn Trạch"],
      ["Khu vực đại diện: Mỹ Tho", "Khu vực đại diện: Tiền Giang"],
    ];
    Object.values(contentRecords).forEach((record) => {
      if (!record?.html) return;
      const exactReplacement = exactReplacements.get(record.html.trim());
      if (exactReplacement) record.html = exactReplacement;
      replacements.forEach(([from, to]) => {
        if (!record.html.includes(to)) record.html = record.html.split(from).join(to);
      });
    });
    persistContentStorage();
    localStorage.setItem(LOCATION_CONTENT_REVISION_KEY, LOCATION_CONTENT_REVISION);
  } catch (error) {
    // Giữ nội dung mặc định trong HTML khi bộ nhớ trình duyệt bị chặn.
  }
}

function migrateMenuContent() {
  try {
    if (localStorage.getItem(MENU_CONTENT_REVISION_KEY) === MENU_CONTENT_REVISION) return;
    Object.keys(contentRecords).forEach((key) => {
      if (key.startsWith("menu-")) delete contentRecords[key];
    });
    persistContentStorage();
    localStorage.setItem(MENU_CONTENT_REVISION_KEY, MENU_CONTENT_REVISION);
  } catch (error) {
    // Giữ nội dung mặc định trong HTML khi bộ nhớ trình duyệt bị chặn.
  }
}

function migrateMenu23kContent() {
  try {
    if (localStorage.getItem(MENU_23K_CONTENT_REVISION_KEY) === MENU_23K_CONTENT_REVISION) return;
    Object.keys(contentRecords).forEach((key) => {
      if (key.startsWith("menu-basic-")) delete contentRecords[key];
    });
    persistContentStorage();
    localStorage.setItem(MENU_23K_CONTENT_REVISION_KEY, MENU_23K_CONTENT_REVISION);
  } catch (error) {
    // Giữ dữ liệu mặc định của suất 23K khi bộ nhớ trình duyệt bị chặn.
  }
}

function migrateQualityProcessContent() {
  try {
    if (localStorage.getItem(QUALITY_PROCESS_CONTENT_REVISION_KEY) === QUALITY_PROCESS_CONTENT_REVISION) return;
    const staleFragments = [
      "AN TOÀN",
      "Kiểm soát nguyên liệu, sơ chế, chế biến, lưu mẫu và vệ sinh bếp trong suốt quá trình vận hành.",
      "Đánh giá nhà cung cấp và hồ sơ nguyên liệu.",
      "Kiểm tra cảm quan, số lượng và nhiệt độ.",
      "Phân khu rõ ràng, hạn chế nhiễm chéo.",
      "Kiểm soát nhiệt và thời gian từng món.",
      "Đúng định lượng, đúng ca, đúng thời điểm.",
      "Ghi nhận, vệ sinh và đối soát hằng ngày.",
    ];
    Object.keys(contentRecords).forEach((key) => {
      const html = contentRecords[key]?.html || "";
      if (staleFragments.some((fragment) => html.includes(fragment))) delete contentRecords[key];
    });
    persistContentStorage();
    localStorage.setItem(QUALITY_PROCESS_CONTENT_REVISION_KEY, QUALITY_PROCESS_CONTENT_REVISION);
  } catch (error) {
    // Giữ nội dung mặc định trong HTML khi bộ nhớ trình duyệt bị chặn.
  }
}

function setContentEditorStatus(message, isError = false) {
  contentEditorStatus.textContent = message;
  contentEditorStatus.classList.toggle("error", isError);
  clearTimeout(contentStatusTimer);
  contentStatusTimer = setTimeout(() => {
    contentEditorStatus.textContent = CONTENT_HELP_TEXT;
    contentEditorStatus.classList.remove("error");
  }, 2200);
}

function contentKeyForElement(element, counters) {
  const partner = element.closest(".partner-logo");
  const partnerSlot = partner?.querySelector("[data-image-slot^='partner-']")?.dataset.imageSlot;
  if (partnerSlot) return `partners-${partnerSlot}-copy`;
  if (element.id) return `id-${element.id}`;
  const scope = element.closest("section[id]")?.id
    || (element.closest(".hero") ? "hero" : "")
    || (element.closest(".intro-strip") ? "intro" : "")
    || (element.closest("footer") ? "footer" : "page");
  const descriptor = [...element.classList].find((name) => !name.startsWith("reveal")) || element.tagName.toLowerCase();
  const counterKey = `${scope}-${descriptor}`;
  const order = (counters.get(counterKey) || 0) + 1;
  counters.set(counterKey, order);
  return `${counterKey}-${String(order).padStart(2, "0")}`;
}

function updateLinkedContent(element, record) {
  if (element.matches(".count") && record.count) {
    element.dataset.count = String(record.count);
    element.textContent = new Intl.NumberFormat("vi-VN").format(record.count);
  }
  const link = element.closest("a[href^='tel:'], a[href^='mailto:']");
  if (!link) return;
  if (link.href.startsWith("tel:")) {
    const digits = element.textContent.replace(/\D/g, "");
    if (digits.length >= 9) link.href = `tel:${digits}`;
  }
  if (link.href.startsWith("mailto:")) {
    const email = element.textContent.trim().match(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/)?.[0];
    if (email) link.href = `mailto:${email}`;
  }
}

function applyContentRecord(key, record) {
  const group = contentGroups.get(key) || [];
  const translatedHtml = translateEditableMenuHtml(sanitizeContentHtml(record.html || ""));
  group.forEach((element) => {
    element.innerHTML = translatedHtml;
    updateLinkedContent(element, record);
  });
}

function applyStoredContentRecords() {
  Object.entries(contentRecords).forEach(([key, record]) => {
    if (contentGroups.has(key) && record?.html !== undefined) applyContentRecord(key, record);
  });
}

function saveContentTarget(target, syncGroup = false) {
  if (!target) return;
  const key = target.dataset.contentKey;
  const html = sanitizeContentHtml(target.innerHTML);
  const record = { html, updatedAt: new Date().toISOString() };
  if (target.matches(".count")) {
    const count = Number(target.textContent.replace(/\D/g, ""));
    if (Number.isFinite(count)) record.count = count;
  }
  contentRecords[key] = record;
  persistContentStorage();
  if (syncGroup) applyContentRecord(key, record);
  contentResetSelected.disabled = false;
  setContentEditorStatus("Đã tự động lưu");
}

function selectContentTarget(target) {
  selectedContentTarget?.classList.remove("content-edit-selected");
  selectedContentTarget = target;
  selectedContentTarget.classList.add("content-edit-selected");
  contentResetSelected.disabled = !contentRecords[target.dataset.contentKey];
}

function registerContentTargets() {
  const counters = new Map();
  document.querySelectorAll(contentTargetSelector).forEach((element) => {
    if (element.closest(".content-editor-bar, .image-manager, .contact-form, [aria-hidden='true']:not(.partner-duplicate)")) return;
    const key = contentKeyForElement(element, counters);
    element.dataset.i18nExact = "";
    element.dataset.contentEditable = "true";
    element.dataset.contentKey = key;
    if (!contentGroups.has(key)) contentGroups.set(key, []);
    contentGroups.get(key).push(element);
    if (!contentOriginals.has(key)) contentOriginals.set(key, sanitizeContentHtml(element.innerHTML));
  });
}

function setContentEditMode(enabled) {
  if (!imageEditorAllowed) return;
  if (enabled && document.body.classList.contains("image-edit-mode")) setImageEditMode(false);
  closeDraftEditorPopover();
  if (enabled && window.QBA_I18N?.getLanguage?.() !== "vi") window.QBA_I18N.setLanguage("vi");
  document.body.classList.toggle("content-edit-mode", enabled);
  contentEditorToggle.classList.toggle("active", enabled);
  contentEditorToggle.setAttribute("aria-pressed", String(enabled));
  contentEditorToggle.querySelector(".editor-toggle-label").textContent = enabled ? "Đóng chữ" : "Nội dung";
  contentEditorBar.classList.toggle("open", enabled);
  contentEditorBar.setAttribute("aria-hidden", String(!enabled));
  document.querySelectorAll("[data-content-editable]").forEach((element) => {
    if (enabled) {
      element.setAttribute("contenteditable", "true");
      element.setAttribute("spellcheck", "true");
    } else {
      element.removeAttribute("contenteditable");
      element.removeAttribute("spellcheck");
      element.classList.remove("content-edit-selected");
    }
  });
  if (!enabled) {
    clearTimeout(contentSaveTimer);
    if (selectedContentTarget) saveContentTarget(selectedContentTarget, true);
    selectedContentTarget = null;
    contentResetSelected.disabled = true;
  } else {
    setContentEditorStatus(CONTENT_HELP_TEXT);
  }
  syncDraftEditorControls();
}

contentEditorToggle.addEventListener("click", () => {
  setContentEditMode(!document.body.classList.contains("content-edit-mode"));
});

contentEditorDone.addEventListener("click", () => {
  setContentEditMode(false);
  contentEditorToggle.focus();
});

document.addEventListener("click", (event) => {
  if (!document.body.classList.contains("content-edit-mode")) return;
  const target = event.target.closest("[data-content-editable]");
  if (!target) return;
  if (target.closest("a, button")) event.preventDefault();
  event.stopPropagation();
  selectContentTarget(target);
  target.focus();
}, true);

document.addEventListener("input", (event) => {
  const target = event.target.closest?.("[data-content-editable]");
  if (!target || !document.body.classList.contains("content-edit-mode")) return;
  selectContentTarget(target);
  clearTimeout(contentSaveTimer);
  contentSaveTimer = setTimeout(() => saveContentTarget(target), 520);
});

document.addEventListener("focusout", (event) => {
  const target = event.target.closest?.("[data-content-editable]");
  if (!target || !document.body.classList.contains("content-edit-mode")) return;
  clearTimeout(contentSaveTimer);
  saveContentTarget(target, true);
});

document.addEventListener("keydown", (event) => {
  if (!document.body.classList.contains("content-edit-mode")) return;
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter" && selectedContentTarget) {
    event.preventDefault();
    selectedContentTarget.blur();
  }
  if (event.key === "Escape") {
    event.preventDefault();
    setContentEditMode(false);
    contentEditorToggle.focus();
  }
});

contentResetSelected.addEventListener("click", () => {
  if (!selectedContentTarget) return;
  const key = selectedContentTarget.dataset.contentKey;
  delete contentRecords[key];
  const original = { html: contentOriginals.get(key) || selectedContentTarget.dataset.contentOriginal || "" };
  if (contentGroups.has(key)) applyContentRecord(key, original);
  else selectedContentTarget.innerHTML = sanitizeContentHtml(original.html);
  persistContentStorage();
  contentResetSelected.disabled = true;
  setContentEditorStatus("Đã khôi phục mục này");
});

contentResetAll.addEventListener("click", () => {
  if (!window.confirm("Khôi phục toàn bộ chữ và số về nội dung ban đầu?")) return;
  contentRecords = {};
  contentOriginals.forEach((html, key) => applyContentRecord(key, { html }));
  persistContentStorage();
  updateMenuDisplay();
  contentResetSelected.disabled = true;
  setContentEditorStatus("Đã khôi phục toàn bộ nội dung");
});

function initializeContentEditor() {
  registerContentTargets();
  contentRecords = getContentStorage();
  migrateAboutContent();
  migrateLocationContent();
  migrateMenuContent();
  migrateMenu23kContent();
  migrateQualityProcessContent();
  contentRecords = { ...productionContentRecords, ...contentRecords };
  applyStoredContentRecords();
  updateMenuDisplay();
}

initializeContentEditor();
document.addEventListener("qba:languagechange", applyStoredContentRecords);
normalizeMenuLineStarts();
document.addEventListener("qba:languagechange", () => normalizeMenuLineStarts());
window.addEventListener("load", () => normalizeMenuLineStarts());
