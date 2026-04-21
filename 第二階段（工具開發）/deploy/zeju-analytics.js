/**
 * 擇居統一追蹤封裝 (zeju-analytics.js)
 * ────────────────────────────────────────────
 * 將所有追蹤呼叫集中，同時轉發給 GA4 + Clarity + Vercel Analytics。
 * 外部只呼叫 window.zeju.track(event, params)，不直接碰底層 SDK。
 *
 * 設計原則：
 *   1. 錯誤容錯：任一 SDK 未載入不影響其他，不得拋錯。
 *   2. 輕量：defer 載入，不阻塞頁面。
 *   3. Debug 友善：?debug=1 或 localStorage.zejuDebug=1 會 console.log 所有事件。
 */

(function () {
  'use strict';

  // ─── Debug 模式 ─────────────────────────────────────
  const DEBUG =
    /[?&]debug=1/.test(location.search) ||
    (function () {
      try { return localStorage.getItem('zejuDebug') === '1'; } catch (_) { return false; }
    })();

  function log() {
    if (DEBUG) {
      // eslint-disable-next-line no-console
      console.log('[zeju]', ...arguments);
    }
  }

  // ─── 核心追蹤函數 ────────────────────────────────────

  /**
   * 發送自訂事件到所有分析平台
   * @param {string} event - 事件名稱（snake_case，如 quiz_completed）
   * @param {object} [params] - 事件參數（會帶到 GA4，Clarity 透過 set 欄位保存）
   */
  function track(event, params) {
    params = params || {};
    log('track', event, params);

    // GA4
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', event, params);
      }
    } catch (e) { log('gtag error', e); }

    // Clarity — 只吃字串名稱，不吃 params。重要的 params 另外用 set 標記
    try {
      if (typeof window.clarity === 'function') {
        window.clarity('event', event);
        // 把關鍵 params 設成 session-level tag，Clarity 可用來篩選 session
        Object.keys(params).forEach(function (k) {
          const v = params[k];
          if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
            window.clarity('set', k, String(v));
          }
        });
      }
    } catch (e) { log('clarity error', e); }

    // dataLayer（GTM 或未來用）
    try {
      if (Array.isArray(window.dataLayer)) {
        window.dataLayer.push({ event: event, ...params });
      }
    } catch (_) { /* ignore */ }
  }

  // ─── 滾動深度追蹤 ───────────────────────────────────

  /**
   * 啟用頁面滾動深度事件（25/50/75/100%）
   * @param {string} eventName - 觸發的事件名（預設 scroll_depth）
   * @param {object} [extraParams] - 每次觸發都會附上的額外參數
   */
  function trackScrollDepth(eventName, extraParams) {
    eventName = eventName || 'scroll_depth';
    extraParams = extraParams || {};
    const fired = { 25: false, 50: false, 75: false, 100: false };

    function check() {
      const docH = Math.max(
        document.documentElement.scrollHeight,
        document.body.scrollHeight
      );
      const winH = window.innerHeight;
      const scrolled = window.scrollY + winH;
      const pct = Math.min(100, Math.round((scrolled / docH) * 100));

      [25, 50, 75, 100].forEach(function (threshold) {
        if (!fired[threshold] && pct >= threshold) {
          fired[threshold] = true;
          track(eventName, Object.assign({}, extraParams, { depth: threshold }));
        }
      });
    }

    let throttled = false;
    window.addEventListener('scroll', function () {
      if (throttled) return;
      throttled = true;
      setTimeout(function () {
        check();
        throttled = false;
      }, 500);
    }, { passive: true });

    // 初次呼叫以處理短頁面
    setTimeout(check, 1500);
  }

  // ─── 停留時間追蹤 ───────────────────────────────────

  /**
   * 在頁面離開時送出 time_on_page 事件
   * @param {string} pageType - 頁面類別（step / builder / guide / etc）
   * @param {object} [extraParams] - 附加參數
   */
  function trackReadingTime(pageType, extraParams) {
    extraParams = extraParams || {};
    const startTime = Date.now();
    let sent = false;

    function send() {
      if (sent) return;
      sent = true;
      const seconds = Math.round((Date.now() - startTime) / 1000);
      track('time_on_page', Object.assign({}, extraParams, {
        page_type: pageType,
        seconds: seconds,
        // 分級：方便 GA4 報表
        bucket: seconds < 15 ? 'bounce'
              : seconds < 60 ? 'brief'
              : seconds < 180 ? 'reading'
              : 'deep_reading'
      }));
    }

    // visibilitychange 比 beforeunload 在行動版更可靠
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') send();
    });
    window.addEventListener('pagehide', send);
  }

  // ─── 外連／內跳連結追蹤 ─────────────────────────────

  /**
   * 綁定所有 <a> 的點擊事件，自動分類內/外連
   * 若連結有 data-track-as="foo"，會用該事件名；否則用 link_click
   */
  function autoTrackLinks() {
    document.addEventListener('click', function (e) {
      const a = e.target.closest('a');
      if (!a || !a.href) return;

      const href = a.getAttribute('href') || '';
      const eventName = a.getAttribute('data-track-as') || 'link_click';
      const params = {
        href: href,
        text: (a.textContent || '').trim().slice(0, 80),
        is_external: /^https?:\/\//.test(href) && !href.includes(location.host)
      };

      // data-track-* 額外屬性全部帶上
      Array.from(a.attributes).forEach(function (attr) {
        if (attr.name.startsWith('data-track-') && attr.name !== 'data-track-as') {
          params[attr.name.replace('data-track-', '')] = attr.value;
        }
      });

      track(eventName, params);
    }, { capture: true });
  }

  // ─── 頁面類別自動偵測（讓事件帶上頁面 context）──────

  function detectPageType() {
    const path = location.pathname;
    if (path === '/' || path.endsWith('/index.html')) return 'home';
    if (path.endsWith('/quiz.html')) return 'tool_quiz';
    if (path.endsWith('/progress.html')) return 'tool_progress';
    if (path.endsWith('/calculator.html')) return 'tool_calculator';
    if (path.endsWith('/tools.html')) return 'tools_hub';
    if (path.endsWith('/builders.html')) return 'builders_list';
    if (/\/builder-[^/]+\.html$/.test(path)) return 'builder_detail';
    if (/\/step\/\d+\.html$/.test(path)) return 'step_page';
    if (path.includes('/guide/')) return 'guide';
    if (/\/quiz-result\//.test(path)) return 'quiz_result';
    if (path.endsWith('/trends.html')) return 'trends';
    if (path.endsWith('/inspection.html')) return 'inspection';
    if (path.endsWith('/about.html')) return 'about';
    if (path.endsWith('/privacy.html')) return 'privacy';
    if (path.endsWith('/terms.html')) return 'terms';
    return 'other';
  }

  // ─── 初始化 ─────────────────────────────────────────

  const pageType = detectPageType();

  // 用 clarity.set 把 page_type 標進 session，之後能在 Clarity 篩選
  try {
    if (typeof window.clarity === 'function') {
      window.clarity('set', 'page_type', pageType);
    }
  } catch (_) { /* ignore */ }

  // 自動綁定外連追蹤
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoTrackLinks);
  } else {
    autoTrackLinks();
  }

  // ─── 對外 API ───────────────────────────────────────

  window.zeju = {
    track: track,
    trackScrollDepth: trackScrollDepth,
    trackReadingTime: trackReadingTime,
    pageType: pageType,
    debug: DEBUG
  };

  log('zeju-analytics ready, pageType=' + pageType);
})();
