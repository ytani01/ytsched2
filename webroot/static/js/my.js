/**
 *   (c) 2021 Yoichi Tanibayashi
 */

/*
 * !! Important !!
 *
 * new Date()の日付の区切り文字が
 *   '/' だとJST(+09:00),
 *   '-' だとUTC
 * とみなされる！
 *
 * (ex.)
 * > (new Date("2021/01/01")).toISOString();
 * < "2020-12-31T15:00:00.000Z"
 * > (new Date("2021-01-01")).toISOString();
 * < "2021-01-01T00:00:00.000Z"
 *
 * ここでは、区切り文字を '-'に揃える
 */

let elOSD1, elOSD2;

const diffDays = [
    -3650, -365, -92, -30, -14, -7, -3, +3, +7, +14, +30, +92, +365, +3650
];

const day2diffY = (d) => {
    const a = 2;
    const b = 50;
    
    if (Math.abs(d) * a < 1) {
        return 0;
    }
    
    const y = Math.round(Math.log10(Math.abs(d) * a) * b);
    if (d < 0) {
        return -y;
    }
    return y;
};

/**
 * @param {bool} on
 */
const dispOSD = (on) => {
    if ( ! on ) {
        elOSD1.style.display = "none";
        elOSD2.style.display = "none";
        elGageR.style.display = "none";
        elGageL.style.display = "none";
        elGageRBase.style.display = "none";
        elGageLBase.style.display = "none";

        for (let [i, d] of diffDays.entries()) {
            elGageR[i].style.display = "none";
            elGageL[i].style.display = "none";
        }
        return;
    }
    const win_h = document.documentElement.clientHeight;
    
    //
    // OSD1
    //
    elOSD1.style.right = "5px";
    elOSD1.style.top = "40px";

    const top_date_str = getTopDateString().split('-').join('/');
    const top_rel_days = getDaysFromToday(top_date_str);
    top_sign_str = '';
    if (top_rel_days > 0) {
        top_sign_str = '+';
    }
    top_w_sign_str = '';
    if (top_rel_days >= 7) {
        top_w_sign_str = '+';
    }
    const top_rel_weeks = parseInt(top_rel_days / 7);
    elOSD1.innerHTML =
        `${top_date_str}<br />` +
        `${top_sign_str}${top_rel_days} days<br /> ` +
        `${top_w_sign_str}${top_rel_weeks} weeks`;
    elOSD1.style.display = "block";

    //
    // OSD2
    //
    elOSD2.style.right = "5px";
    elOSD2.style.bottom = "80px";

    const bottom_date_str = getBottomDateString().split('-').join('/');
    const bottom_rel_days = getDaysFromToday(bottom_date_str);
    bottom_sign_str = '';
    if (bottom_rel_days > 0) {
        bottom_sign_str = '+';
    }
    bottom_w_sign_str = '';
    if (bottom_rel_days >= 7) {
        bottom_w_sign_str = '+';
    }
    const bottom_rel_weeks = parseInt(bottom_rel_days / 7);
    elOSD2.innerHTML =
        `${bottom_date_str}<br />` +
        `${bottom_sign_str}${bottom_rel_days} days<br /> ` +
        `${bottom_w_sign_str}${bottom_rel_weeks} weeks`;

    elOSD2.style.display = "block";

    //
    // gage
    //
    elGageR.style.display = "block";
    elGageL.style.display = "block";
    elGageRBase.style.display = "block";
    elGageLBase.style.display = "block";

    for (let [i, d] of diffDays.entries()) {
        elGageR[i].style.display = "block";
        elGageL[i].style.display = "block";
    }

    const gageH = elGageL.clientHeight;
    
    const diffY = day2diffY(top_rel_days);;
    // console.log(`diffY=${diffY}`);

    const gageBaseBottom = win_h / 2 - gageH / 2;
    const gageBottom = gageBaseBottom - diffY;

    elGageR.style.bottom = `${gageBottom}px`;
    elGageL.style.bottom = `${gageBottom}px`;

    elGageRBase.style.bottom = `${gageBaseBottom}px`;
    elGageLBase.style.bottom = `${gageBaseBottom}px`;

    const gageH1 = elGageL[0].clientHeight;

    for (let [i, d] of diffDays.entries()) {
        let bottom = win_h / 2 - gageH1 / 2 - day2diffY(d) + 1;
        elGageR[i].style.bottom = `${bottom}px`;
        elGageL[i].style.bottom = `${bottom}px`;
    }
};

/**
 * 日数計算
 *
 * @param {Date} d_from
 * @param {Date} d_to
 *
 * @return {number} days
 */
const calcDays = (d_from, d_to) => {
    const days = (d_to - d_from) / (24 * 60 * 60* 1000);
    return days;
};

/**
 * 日付をずらす
 *
 * @param {Date} d
 * @param {number} days
 *
 * @return {Date} d
 */
const shiftDays = (d, days) => {
    d.setDate(d.getDate() + days);
    return d;
};

/**
 * get JST string: "YYYY-mm-ddTHH:MM:SS.SSSZ"
 *
 * `toLocaleDateString`が機能しない環境があるので、
 * あえて、面倒な変換を行う(!?)
 *
 * @param {Date} d
 *
 * @return {String} jst_str
 */
const getJSTString = (d) => {
    tz_msec = d.getTimezoneOffset() / 60 * 3600 * 1000;
    const jst_str = (new Date(d.getTime() - tz_msec)).toISOString();
    return jst_str;
};

/**
 * get JST date string: "YYYY-mm-dd"
 *
 * @param {Date} d
 *
 * @return {String} jst_date_str
 */
const getJSTDateString = (d) => {
    return getJSTString(d).replace(/T.*$/, '');
};

/**
 *
 * @return {String} date_str: "date-YYYY-MM-DD"
 */
const getTopDateString = () => {
    const el_date_from = document.getElementById("date_from");
    const win_top = window.pageYOffset;

    let el_date = document.getElementById(`date-${el_date_from.value}`);
    while ( el_date.offsetTop < win_top ) {
        const d1 = new Date(el_date.id.replace('date-',''));
        const d1_str = getJSTDateString(shiftDays(d1, 1));
        el_date = document.getElementById(`date-${d1_str}`);
    }
    return el_date.id.replace('date-', '');
};

/**
 *
 * @return {String} date_str: "date-YYYY-MM-DD"
 */
const getBottomDateString = () => {
    const el_date_to = document.getElementById("date_to");
    const win_bottom = window.pageYOffset
          + document.documentElement.clientHeight;

    let el_date = document.getElementById(`date-${el_date_to.value}`);
    // console.log(`getBottomDate: el_date.id=${el_date.id}`);
    while ( el_date.offsetTop + el_date.offsetHeight > win_bottom ) {
        const d1 = new Date(el_date.id.replace('date-',''));
        const d1_str = getJSTDateString(shiftDays(d1, -1));
        el_date = document.getElementById(`date-${d1_str}`);
    }
    return el_date.id.replace('date-', '');
};

/**
 * @return {number} days
 */
const getDaysFromToday = (date_str) => {
    /*
     * !! Important !!
     *
     * new Date()の日付の区切り文字が '/' だとJST, '-'だとUTC !!
     * 区切り文字を '-'に揃える
     */
    const d_date = new Date(date_str.split('/').join('-'));
    const d_today = new Date(getJSTDateString(new Date()));
    const days = calcDays(d_today, d_date);
    return days;
};

/**
 *
 */
const doPost = (path, data) => {
    console.log(`doPost()`);

    const form = document.createElement("form");
    form.setAttribute("action", path);
    form.setAttribute("method", "POST");
    form.style.display = "none";
    document.body.appendChild(form);

    if (data !== undefined) {
        for (let param in data) {
            const input = document.createElement("input");
            input.setAttribute("type", "hidden");
            input.setAttribute("name", param);
            input.setAttribute("value", data[param]);
            form.appendChild(input);
        }
    }
    form.submit();
};

/**
 *
 */
const doPostDate = (path, date, days = 0, sde_align = undefined) => {
    console.log(`doPostDate: sde_align=${sde_align}`);
    let d1 = new Date(date);
    d1 = shiftDays(d1, days);
    d1_str = getJSTDateString(d1);
    console.log(`date=${date}, d1_str=${d1_str}`);

    data_obj = {date: d1_str};
    if ( sde_align ) {
        data_obj["sde_align"] = sde_align;
    }
    doPost(path, {date: d1_str});
};

/**
 *
 */
const doGet = (path, data) => {
    let url = `${location.protocol}//${location.host}${path}?`;

    for (let param in data) {
        url += `${param}=${data[param]}&`;
    }
    url = url.replace(/&$/, '');
    console.log(`url=${url}`);
    window.location.href=url;
};

let scrollFlag = false;

/**
 *
 */
const scrollHdr = (event) => {
    dispOSD(false);

    const top_date_str = getTopDateString();
    const rel_days = getDaysFromToday(top_date_str);
    const el_rel_days = document.getElementById("rel_days");
    yyyy_str = top_date_str.substr(0,4);
    mm_dd_str = top_date_str.substr(5,5).replace('-','/');
    sign_str = '';

    const rel_weeks = parseInt(rel_days / 7);
    if (rel_weeks >= 0) {
        sign_str = '+';
    }
    el_rel_days.innerHTML
        = `${yyyy_str}<br />[${sign_str}${rel_weeks}w]`;

    if ( ! scrollFlag ) {
        console.log(`scrollHdr:event=${event}, scrollFlag=${scrollFlag}`);
        return;
    }

    const el_search = document.getElementById("search_str");
    //console.log(`onscroll:search_str="${el_search.value}"`);
    if (el_search.value != "") {
        return;
    }

    const win_h = document.documentElement.clientHeight;
    const body_h = document.body.clientHeight;
    const d_top = window.pageYOffset;
    const d_bottom = body_h - d_top - win_h;
    console.log(`scrollHdr:d_top=${d_top}, d_bottom=${d_bottom}`);
    
    if (d_top < 50) {
        scrollFlag = false;
        el = document.getElementById("date_from");
        date = el.value;
        console.log(`date=${date}`);
        doPost('/ytsched/', {date: date, sde_align: "top"});
    }
    if (d_bottom < 80) {
        scrollFlag = false;
        el = document.getElementById("date_to");
        date = el.value;
        console.log(`date=${date}`);
        doPost('/ytsched/', {date: date, sde_align: "bottom"});
    }
};

/**
 *
 */
let scrollHdrTimer = 0;
const scrollHdr0 = (event) => {
    dispOSD(true);

    if (scrollHdrTimer > 0) {
        clearTimeout(scrollHdrTimer);
    }
    scrollHdrTimer = setTimeout(scrollHdr, 1000);
};

/**
 *
 */
const scrollToId = (id, sde_align = "top", behavior = "smooth") => {
    scrollFlag = false;
    console.log(`scrollToId:id=${id}`);
    

    const body_h = document.body.clientHeight;
    const win_h = document.documentElement.clientHeight;

    el_main = document.getElementById("main");
    el_main.style.visibility = "visible";
    if (body_h <= win_h) {
        console.log(`body_h=${body_h} < win_h=${win_h}`);
        return true;
    }

    const el = document.getElementById(id);
    const el_search = document.getElementById('search_str');
    const search_str = el_search.value;

    if (el == null) {
        console.log(`scrollToId:scrollToID:el=${el}`);

        if (search_str) {
            return true;
        }
        return false;
    }

    const top_of_el = el.offsetTop;
    const bottom_of_el = el.offsetTop + el.offsetHeight;
    const el_menu_bar = document.getElementById("menu_bar");
    const menu_bar_h = el_menu_bar.offsetHeight;

    console.log(`scrollToId:sde_align=${sde_align}`);

    const scroll_offset = 30;
    if (sde_align == "top") {
        scrollTo({left: 0,
                  top: top_of_el - scroll_offset,
                  behavior: behavior});
    }
    if (sde_align == "bottom") {
        scrollTo({left: 0,
                  top: bottom_of_el - win_h + menu_bar_h + scroll_offset,
                  behavior: behavior});
    }

    scrollFlag = true;
    return true;
};

/**
 *
 */
const scrollToDate = (path, date, sde_align="top", behavior="smooth") => {
    scrollFlag = false;
    console.log(`scrollToDate:date=${date}, sde_align=${sde_align}`);
    
    const el_cur_day = document.getElementById("cur_day");

    if (scrollToId(`date-${date}`, sde_align, behavior)) {
        el_cur_day.value = date;
        scrollFlag = true;
        return true;
    }

    console.log(`path=${path}`);
    doPost(path, {date: date, sde_align: sde_align});
    return false;
};

/*
 *
const moveDays = (path, days, behavior="smooth") => {
    const el = document.getElementById("cur_day");
    let d1 = new Date(el.value);
    d1 = shiftDays(d1, days);
    console.log(`moveDays:d1=${d1}`);

    d1_str = getJSTDateString(d1);
    console.log(`moveDays:d1_str=${d1_str}`);
    el.value = d1_str;
    scrollToDate(path, d1_str, "top", behavior);
};
 */

/**
 * [Important!]
 * スクロールによる自動読み込みより先に、自動読み込みをトリガー
 *
 * @param {number} direction
 * @param {String} path
 * @param {String} behavior
 */
const moveToMonday = (direction=1, path, behavior="smooth") => {
    const el_cur_day = document.getElementById("cur_day");
    let cur_day = new Date(el_cur_day.value);
    console.log(`moveToMonday:path=${path}`);
    console.log(`moveToMonday:cur_day=${getJSTString(cur_day)}`);

    let wday = cur_day.getDay(); // 0:Sun, 1:Mon, ..
    if (wday == 0) {
        wday = 7; // Sun: 0 --> 7
    }

    let days;
    let days2;
    if ( direction > 0 ) {
        days = 8 - wday;
        days2 = days + 21;
    } else {
        days = 1 - wday;
        if (days == 0) {
            days = -7; // Mon
        }
        days2 = days - 14;
    }
    console.log(`moveToMonday:days=${days}, days2=${days2}`);
    
    let d1 = new Date(el_cur_day.value);
    d1 = shiftDays(d1, days);
    d1_str = getJSTDateString(d1);
    console.log(`moveToMonday:d1_str=${d1_str}`);

    let d2 = new Date(el_cur_day.value);
    d2 = shiftDays(d2, days2);
    d2_str = getJSTDateString(d2);
    console.log(`moveToMonday:d2_str=${d2_str}`);

    el_d2 = document.getElementById(`date-${d2_str}`);
    if ( ! el_d2 ) {
        doPost(path, {date: d1_str, sde_align: "top"});
        return;
    }

    el_cur_day.value = d1_str;
    scrollFlag = false;
    scrollToId(`date-${d1_str}`);
};

/**
 * TBD
 */
const editStr = (el0) => {
    console.log(`el0=${el0}`);
    let value = el0.innerHTML;
    console.log(`value=${value}`);
    const el_input = document.createElement("input");
    el_input.type="text";
    el_input.value = value;
    console.log(`el_input=${el_input.type}`);

    el0.replaceChildren(el_input);
    el0.onclick="";
    el0.onchange= () => {
        console.log(`value=${el_input.value}`);
    };
};
