/**
 * simple chat
 *
 *   (c) 2021 Yoichi Tanibayashi
 */
const ID_MSG_AREA = "message_area";
const ID_MY_NAME = "my_name";
const ID_MY_MSG = "my_msg";

const cookieObj = new MyCookie();
let myName = "";

/**
 * 'http://host:port/aaa/bbb/' -> 'ws://host:port/aaa/ws'
 * 'https://host:port/aaa/bbb/' -> 'wss://host:port/aaa/ws'
 */
const WS_PROTO = location.protocol.replace('http', 'ws');
const WS_URL = `${WS_PROTO}//${location.host}/`
      + `${location.pathname.split('/')[1]}/ws/`;
console.log(`WS_URL=${WS_URL}`);

/**
 * websocket は、常に open の状態にして、メッセージ待ち受ける
 *
 *  - ``window.onload``, ``ws.onclose`` で、``connect_ws()``
 *  - 送信時は、いきなり ``ws.send()``
 */
let wsObj = undefined;

/**
 *
 */
const connect_ws = () => {
    wsObj = new WebSocket(WS_URL);

    wsObj.onclose = () => {
        console.log(`onclose()`);
        const el = document.getElementById(ID_MSG_AREA);
        el.value = '';
        connect_ws();  // reconnect
    };

    wsObj.onmessage = (event) => {
        const msg = event.data;
        console.log(`onmessage(): msg=${msg}`);

        const el = document.getElementById(ID_MSG_AREA);
        el.value += msg;
        el.scrollTop = el.scrollHeight; // 最下部にスクロールする
    };
};

/**
 * @param {string} msg_id
 */
const send_msg = () => {
    const el_msg = document.getElementById(ID_MY_MSG);
    wsObj.send(`${myName}>${el_msg.value}`);
    el_msg.value = '';
};

/**
 * @param {string} name_id
 */
const set_name = () => {
    const el_name = document.getElementById(ID_MY_NAME);
    myName = el_name.value;
    console.log(`set_name("${ID_MY_NAME}"): ${myName}`);
    cookieObj.set(ID_MY_NAME, myName);
};

/**
 *
 */
window.onload = () => {
    console.log(`window.onload()`);

    connect_ws();

    myName = cookieObj.get(ID_MY_NAME);
    if (myName === undefined) {
        myName = "";
    }
    console.log(`window.onload(): myName=${myName}`);

    const el_name = document.getElementById(ID_MY_NAME);
    el_name.value = myName;
};
