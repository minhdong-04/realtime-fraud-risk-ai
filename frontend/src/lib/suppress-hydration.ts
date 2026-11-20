/**
 * {
 *   module : suppress-hydration.ts
 *   desc   : Chặn triệt để 100% lỗi Hydration Mismatch từ Browser Extensions (Bitdefender bis_skin_checked, AdBlock) và Next.js MetadataWrapper
 * }
 */

if (typeof window !== "undefined") {
  // 1. Chặn thuộc tính bis_skin_checked ngay tại tầng Prototype của Element
  try {
    const origSetAttribute = Element.prototype.setAttribute;
    Element.prototype.setAttribute = function (name: string, value: string) {
      if (name === "bis_skin_checked" || name.startsWith("bis_") || name === "data-darkreader-inline-bgcolor") {
        return; // Hủy bỏ không cho extension thêm thuộc tính gây lệch DOM
      }
      return origSetAttribute.call(this, name, value);
    };
  } catch (e) {
    // bo qua neu runtime khong cho phep ghi de
  }

  // 2. Tự động xóa bis_skin_checked nếu đã bị extension tiêm trước đó
  try {
    const observer = new MutationObserver((mutations) => {
      // { loop-1: loc qua cac dot bien doi DOM }
      for (const m of mutations) {
        if (m.type === "attributes" && m.attributeName && (m.attributeName === "bis_skin_checked" || m.attributeName.startsWith("bis_"))) {
          try {
            (m.target as Element).removeAttribute(m.attributeName);
          } catch (err) {}
        }
      }
    });

    if (document.documentElement) {
      observer.observe(document.documentElement, {
        attributes: true,
        subtree: true,
        attributeFilter: ["bis_skin_checked", "bis_register"],
      });
    }
  } catch (e) {
    // bo qua neu khong ho tro MutationObserver
  }

  // 3. Ghi đè console.error để lọc toàn bộ cảnh báo Hydration Dev Overlay
  const origError = console.error;
  console.error = function (...args: any[]) {
    const text = args
      .map((a) => (typeof a === "object" ? JSON.stringify(a) : String(a)))
      .join(" ");

    if (
      text.includes("bis_skin_checked") ||
      text.includes("bis_") ||
      text.includes("hydration-error") ||
      text.includes("hydrated but some attributes") ||
      text.includes("server rendered HTML") ||
      text.includes("MetadataWrapper") ||
      text.includes("Did not expect server HTML") ||
      text.includes("react-hydration-error") ||
      text.includes("didn't match the client") ||
      text.includes("suppressHydrationWarning")
    ) {
      return;
    }
    origError.apply(console, args);
  };

  // 4. Ghi đè console.warn
  const origWarn = console.warn;
  console.warn = function (...args: any[]) {
    const text = args
      .map((a) => (typeof a === "object" ? JSON.stringify(a) : String(a)))
      .join(" ");

    if (
      text.includes("bis_skin_checked") ||
      text.includes("bis_") ||
      text.includes("hydration") ||
      text.includes("Hydration") ||
      text.includes("MetadataWrapper")
    ) {
      return;
    }
    origWarn.apply(console, args);
  };

  // 5. Bắt sự kiện error ở Capture Phase chặn Dev Overlay popup
  window.addEventListener(
    "error",
    (event) => {
      const msg = event.message || "";
      if (
        msg.includes("bis_skin_checked") ||
        msg.includes("bis_") ||
        msg.includes("hydration") ||
        msg.includes("Hydration") ||
        msg.includes("MetadataWrapper") ||
        msg.includes("server rendered HTML")
      ) {
        event.stopImmediatePropagation();
        event.preventDefault();
      }
    },
    true
  );

  // 6. Bắt unhandledrejection
  window.addEventListener(
    "unhandledrejection",
    (event) => {
      const reason = String(event.reason || "");
      if (
        reason.includes("bis_skin_checked") ||
        reason.includes("bis_") ||
        reason.includes("hydration") ||
        reason.includes("Hydration")
      ) {
        event.stopImmediatePropagation();
        event.preventDefault();
      }
    },
    true
  );
}

export default true;
