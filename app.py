import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌깨기",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 벽돌깨기 게임")
st.caption("키보드 ← → 로 패들을 움직이거나 마우스로 조작하세요.")

game_html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">

<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        padding: 0;
        background: #0f172a;
        font-family: Arial, sans-serif;
        color: white;
        overflow: hidden;
    }

    #game-container {
        width: 100%;
        max-width: 720px;
        margin: auto;
        text-align: center;
    }

    #info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        font-size: 16px;
        font-weight: bold;
    }

    #gameCanvas {
        display: block;
        width: 100%;
        max-width: 720px;
        height: auto;
        background:
            radial-gradient(circle at top, #1e293b, #020617);
        border: 2px solid #38bdf8;
        border-radius: 10px;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.25);
        touch-action: none;
    }

    #controls {
        margin-top: 10px;
        display: flex;
        justify-content: center;
        gap: 12px;
    }

    button {
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        background: #2563eb;
        color: white;
        font-size: 15px;
        cursor: pointer;
    }

    button:hover {
        background: #1d4ed8;
    }

    #message {
        margin-top: 8px;
        min-height: 24px;
        color: #facc15;
        font-weight: bold;
    }
</style>
</head>

<body>

<div id="game-container">

    <div id="info">
        <span>점수: <span id="score">0</span></span>
        <span>목숨: <span id="lives">3</span></span>
        <span>레벨: <span id="level">1</span></span>
    </div>

    <canvas id="gameCanvas" width="720" height="520"></canvas>

    <div id="message"></div>

    <div id="controls">
        <button id="startBtn">게임 시작</button>
        <button id="pauseBtn">일시정지</button>
        <button id="restartBtn">다시 시작</button>
    </div>

</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreElement = document.getElementById("score");
const livesElement = document.getElementById("lives");
const levelElement = document.getElementById("level");
const messageElement = document.getElementById("message");

const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const restartBtn = document.getElementById("restartBtn");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

// ===============================
// 게임 상태
// ===============================

let score = 0;
let lives = 3;
let level = 1;

let gameRunning = false;
let gamePaused = false;
let gameOver = false;

let animationId = null;

// ===============================
// 패들
// ===============================

const paddle = {
    width: 110,
    height: 14,
    x: WIDTH / 2 - 55,
    y: HEIGHT - 35,
    speed: 8,
    dx: 0
};

// ===============================
// 공
// ===============================

const ball = {
    radius: 8,
    x: WIDTH / 2,
    y: HEIGHT - 60,
    speed: 5,
    dx: 4,
    dy: -4
};

// ===============================
// 벽돌
// ===============================

const brickSettings = {
    rows: 5,
    cols: 10,
    width: 60,
    height: 20,
    padding: 8,
    offsetTop: 55,
    offsetLeft: 25
};

let bricks = [];

// ===============================
// 키 입력
// ===============================

const keys = {
    left: false,
    right: false
};

document.addEventListener("keydown", (event) => {

    if (event.key === "ArrowLeft") {
        keys.left = true;
        event.preventDefault();
    }

    if (event.key === "ArrowRight") {
        keys.right = true;
        event.preventDefault();
    }

    if (event.code === "Space") {
        if (gameRunning) {
            togglePause();
        }
        event.preventDefault();
    }
});

document.addEventListener("keyup", (event) => {

    if (event.key === "ArrowLeft") {
        keys.left = false;
    }

    if (event.key === "ArrowRight") {
        keys.right = false;
    }
});

// ===============================
// 마우스 조작
// ===============================

canvas.addEventListener("mousemove", (event) => {

    const rect = canvas.getBoundingClientRect();

    const scaleX = WIDTH / rect.width;

    const mouseX =
        (event.clientX - rect.left) * scaleX;

    paddle.x = mouseX - paddle.width / 2;

    keepPaddleInside();
});

// ===============================
// 터치 조작
// ===============================

canvas.addEventListener("touchmove", (event) => {

    event.preventDefault();

    const rect = canvas.getBoundingClientRect();

    const scaleX = WIDTH / rect.width;

    const touchX =
        (event.touches[0].clientX - rect.left) * scaleX;

    paddle.x = touchX - paddle.width / 2;

    keepPaddleInside();

}, { passive: false });

// ===============================
// 벽돌 생성
// ===============================

function createBricks() {

    bricks = [];

    const colors = [
        "#ef4444",
        "#f97316",
        "#eab308",
        "#22c55e",
        "#06b6d4",
        "#3b82f6",
        "#8b5cf6"
    ];

    for (let row = 0; row < brickSettings.rows; row++) {

        bricks[row] = [];

        for (let col = 0; col < brickSettings.cols; col++) {

            bricks[row][col] = {
                x: 0,
                y: 0,
                alive: true,
                color: colors[row % colors.length]
            };
        }
    }
}

// ===============================
// 공 초기화
// ===============================

function resetBall() {

    ball.x = WIDTH / 2;
    ball.y = HEIGHT - 60;

    const direction =
        Math.random() > 0.5 ? 1 : -1;

    const speed =
        4 + Math.min(level * 0.5, 3);

    ball.speed = speed;

    ball.dx = direction * speed;
    ball.dy = -speed;
}

// ===============================
// 게임 초기화
// ===============================

function resetGame() {

    score = 0;
    lives = 3;
    level = 1;

    gameRunning = false;
    gamePaused = false;
    gameOver = false;

    paddle.x = WIDTH / 2 - paddle.width / 2;

    createBricks();
    resetBall();

    updateUI();

    messageElement.textContent =
        "게임 시작 버튼을 눌러주세요.";

    draw();
}

// ===============================
// 게임 시작
// ===============================

function startGame() {

    if (gameOver) {
        resetGame();
    }

    if (!gameRunning) {

        gameRunning = true;
        gamePaused = false;

        messageElement.textContent = "";

        cancelAnimationFrame(animationId);

        gameLoop();
    }
}

// ===============================
// 일시정지
// ===============================

function togglePause() {

    if (!gameRunning || gameOver) {
        return;
    }

    gamePaused = !gamePaused;

    if (gamePaused) {

        messageElement.textContent =
            "⏸ 일시정지";

    } else {

        messageElement.textContent = "";

        gameLoop();
    }
}

// ===============================
// 패들 이동
// ===============================

function updatePaddle() {

    if (keys.left) {
        paddle.x -= paddle.speed;
    }

    if (keys.right) {
        paddle.x += paddle.speed;
    }

    keepPaddleInside();
}

function keepPaddleInside() {

    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > WIDTH) {
        paddle.x = WIDTH - paddle.width;
    }
}

// ===============================
// 공 이동
// ===============================

function updateBall() {

    ball.x += ball.dx;
    ball.y += ball.dy;

    // 왼쪽 벽
    if (ball.x - ball.radius <= 0) {

        ball.x = ball.radius;
        ball.dx = Math.abs(ball.dx);
    }

    // 오른쪽 벽
    if (ball.x + ball.radius >= WIDTH) {

        ball.x = WIDTH - ball.radius;
        ball.dx = -Math.abs(ball.dx);
    }

    // 위쪽 벽
    if (ball.y - ball.radius <= 0) {

        ball.y = ball.radius;
        ball.dy = Math.abs(ball.dy);
    }

    // 패들과 충돌
    if (
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <= paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.dy > 0
    ) {

        const hitPosition =
            (ball.x - paddle.x) / paddle.width;

        const angle =
            (hitPosition - 0.5) * Math.PI * 0.8;

        const speed =
            Math.sqrt(
                ball.dx * ball.dx +
                ball.dy * ball.dy
            );

        ball.dx = Math.sin(angle) * speed;
        ball.dy = -Math.cos(angle) * speed;

        ball.y = paddle.y - ball.radius;
    }

    // 바닥
    if (ball.y - ball.radius > HEIGHT) {

        loseLife();
    }

    checkBrickCollision();
}

// ===============================
// 벽돌 충돌
// ===============================

function checkBrickCollision() {

    for (let row = 0; row < brickSettings.rows; row++) {

        for (let col = 0; col < brickSettings.cols; col++) {

            const brick = bricks[row][col];

            if (!brick.alive) {
                continue;
            }

            const brickX =
                brickSettings.offsetLeft +
                col *
                (brickSettings.width + brickSettings.padding);

            const brickY =
                brickSettings.offsetTop +
                row *
                (brickSettings.height + brickSettings.padding);

            brick.x = brickX;
            brick.y = brickY;

            if (
                ball.x + ball.radius > brickX &&
                ball.x - ball.radius <
                    brickX + brickSettings.width &&
                ball.y + ball.radius > brickY &&
                ball.y - ball.radius <
                    brickY + brickSettings.height
            ) {

                brick.alive = false;

                score += 10;

                ball.dy *= -1;

                updateUI();

                if (checkLevelClear()) {
                    nextLevel();
                }

                return;
            }
        }
    }
}

// ===============================
// 레벨 클리어 확인
// ===============================

function checkLevelClear() {

    for (let row = 0; row < brickSettings.rows; row++) {

        for (let col = 0; col < brickSettings.cols; col++) {

            if (bricks[row][col].alive) {
                return false;
            }
        }
    }

    return true;
}

// ===============================
// 다음 레벨
// ===============================

function nextLevel() {

    level++;

    createBricks();

    resetBall();

    messageElement.textContent =
        "🎉 레벨 " + level + " 시작!";

    updateUI();
}

// ===============================
// 목숨 감소
// ===============================

function loseLife() {

    lives--;

    updateUI();

    if (lives <= 0) {

        endGame();

        return;
    }

    resetBall();

    messageElement.textContent =
        "공을 놓쳤습니다! 남은 목숨: " + lives;
}

// ===============================
// 게임 종료
// ===============================

function endGame() {

    gameRunning = false;
    gameOver = true;

    messageElement.textContent =
        "💀 게임 오버! 최종 점수: " + score;

    cancelAnimationFrame(animationId);

    draw();
}

// ===============================
// UI 업데이트
// ===============================

function updateUI() {

    scoreElement.textContent = score;
    livesElement.textContent = lives;
    levelElement.textContent = level;
}

// ===============================
// 배경
// ===============================

function drawBackground() {

    const gradient =
        ctx.createLinearGradient(
            0, 0,
            0, HEIGHT
        );

    gradient.addColorStop(0, "#111827");
    gradient.addColorStop(1, "#020617");

    ctx.fillStyle = gradient;

    ctx.fillRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );
}

// ===============================
// 패들 그리기
// ===============================

function drawPaddle() {

    const gradient =
        ctx.createLinearGradient(
            paddle.x,
            paddle.y,
            paddle.x,
            paddle.y + paddle.height
        );

    gradient.addColorStop(0, "#38bdf8");
    gradient.addColorStop(1, "#2563eb");

    ctx.fillStyle = gradient;

    ctx.beginPath();

    ctx.roundRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height,
        7
    );

    ctx.fill();

    ctx.shadowColor = "#38bdf8";
    ctx.shadowBlur = 15;

    ctx.fill();

    ctx.shadowBlur = 0;
}

// ===============================
// 공 그리기
// ===============================

function drawBall() {

    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "#f8fafc";

    ctx.shadowColor = "#ffffff";
    ctx.shadowBlur = 15;

    ctx.fill();

    ctx.shadowBlur = 0;
}

// ===============================
// 벽돌 그리기
// ===============================

function drawBricks() {

    for (let row = 0; row < brickSettings.rows; row++) {

        for (let col = 0; col < brickSettings.cols; col++) {

            const brick = bricks[row][col];

            if (!brick.alive) {
                continue;
            }

            const x =
                brickSettings.offsetLeft +
                col *
                (brickSettings.width + brickSettings.padding);

            const y =
                brickSettings.offsetTop +
                row *
                (brickSettings.height + brickSettings.padding);

            brick.x = x;
            brick.y = y;

            ctx.fillStyle = brick.color;

            ctx.beginPath();

            ctx.roundRect(
                x,
                y,
                brickSettings.width,
                brickSettings.height,
                4
            );

            ctx.fill();

            ctx.strokeStyle =
                "rgba(255,255,255,0.3)";

            ctx.stroke();
        }
    }
}

// ===============================
// 게임 그리기
// ===============================

function draw() {

    drawBackground();

    drawBricks();

    drawPaddle();

    drawBall();
}

// ===============================
// 게임 업데이트
// ===============================

function update() {

    if (!gameRunning || gamePaused) {
        return;
    }

    updatePaddle();

    updateBall();
}

// ===============================
// 게임 루프
// ===============================

function gameLoop() {

    update();

    draw();

    if (gameRunning && !gamePaused) {

        animationId =
            requestAnimationFrame(gameLoop);
    }
}

// ===============================
// 버튼 이벤트
// ===============================

startBtn.addEventListener(
    "click",
    startGame
);

pauseBtn.addEventListener(
    "click",
    togglePause
);

restartBtn.addEventListener(
    "click",
    () => {
        cancelAnimationFrame(animationId);
        resetGame();
    }
);

// ===============================
// 초기 실행
// ===============================

resetGame();

</script>

</body>
</html>
"""

components.html(
    game_html,
    height=650,
    scrolling=False
)
