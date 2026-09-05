import streamlit as st
import random
import time
import math
import io
import wave
import struct
import base64


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Aditya's Games World",
    page_icon="🎮",
    layout="centered"
)


# ============================================================
# GAME SETTINGS
# ============================================================

TOTAL_ROUNDS = 10

WEAPONS = {
    "rock": "🪨",
    "paper": "📄",
    "scissor": "✂️"
}


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "started": False,
    "round": 1,
    "user_wins": 0,
    "computer_wins": 0,
    "draws": 0,
    "user_choice": None,
    "computer_choice": None,
    "battle_started": False,
    "result_shown": False,
    "game_over": False
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CREATE PIANO MUSIC
# ============================================================

def create_piano():

    sample_rate = 44100
    duration = 8.0

    audio = io.BytesIO()

    with wave.open(audio, "wb") as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        frames = []

        notes = [
            261.63,
            293.66,
            329.63,
            392.00,
            440.00,
            392.00,
            329.63,
            293.66
        ]

        note_length = duration / len(notes)

        for i in range(int(sample_rate * duration)):

            t = i / sample_rate

            note_index = int(
                t / note_length
            )

            if note_index >= len(notes):
                note_index = len(notes) - 1

            frequency = notes[note_index]

            local_time = t % note_length

            fundamental = math.sin(
                2 * math.pi * frequency * t
            )

            harmonic2 = 0.35 * math.sin(
                2 * math.pi * frequency * 2 * t
            )

            harmonic3 = 0.15 * math.sin(
                2 * math.pi * frequency * 3 * t
            )

            sound = (
                fundamental
                + harmonic2
                + harmonic3
            )

            attack = min(
                local_time / 0.03,
                1.0
            )

            decay = math.exp(
                -2.5 * local_time
            )

            envelope = attack * decay

            value = (
                sound
                * envelope
                * 0.18
            )

            value = max(
                -1.0,
                min(1.0, value)
            )

            frames.append(
                struct.pack(
                    "<h",
                    int(value * 30000)
                )
            )

        wav.writeframes(
            b"".join(frames)
        )

    audio.seek(0)

    return audio.getvalue()


# ============================================================
# CREATE BOOM SOUND
# ============================================================

def create_boom():

    sample_rate = 44100
    duration = 1.0

    audio = io.BytesIO()

    with wave.open(audio, "wb") as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        frames = []

        for i in range(
            int(sample_rate * duration)
        ):

            t = i / sample_rate

            # Sharp impact
            impact = (
                math.exp(-80 * t)
                * (
                    math.sin(
                        2 * math.pi * 1600 * t
                    )
                    + 0.7 * math.sin(
                        2 * math.pi * 2700 * t
                    )
                    + 0.4 * math.sin(
                        2 * math.pi * 4300 * t
                    )
                )
            )

            # Deep boom
            boom = (
                math.exp(-6 * t)
                * (
                    math.sin(
                        2 * math.pi * 55 * t
                    )
                    + 0.55 * math.sin(
                        2 * math.pi * 90 * t
                    )
                    + 0.30 * math.sin(
                        2 * math.pi * 130 * t
                    )
                )
            )

            # Punch
            punch = (
                math.exp(-24 * t)
                * math.sin(
                    2 * math.pi * 120 * t
                )
            )

            # Echo
            if t > 0.20:

                echo_time = t - 0.20

                echo = (
                    math.exp(-8 * echo_time)
                    * math.sin(
                        2 * math.pi * 180 * echo_time
                    )
                )

            else:

                echo = 0

            value = (
                0.72 * impact
                + 0.78 * boom
                + 0.35 * punch
                + 0.20 * echo
            )

            value = max(
                -1.0,
                min(1.0, value)
            )

            frames.append(
                struct.pack(
                    "<h",
                    int(value * 30000)
                )
            )

        wav.writeframes(
            b"".join(frames)
        )

    audio.seek(0)

    return audio.getvalue()


PIANO_SOUND = create_piano()
BOOM_SOUND = create_boom()

PIANO_BASE64 = base64.b64encode(
    PIANO_SOUND
).decode("utf-8")


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 10%, #4937a8 0%, transparent 30%),
        radial-gradient(circle at 90% 15%, #852d86 0%, transparent 30%),
        radial-gradient(circle at 50% 100%, #007f83 0%, transparent 35%),
        linear-gradient(135deg, #050817, #101735, #070a18);
}

.game-title {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    color: white;
    margin-top: 10px;
    margin-bottom: 5px;
    text-shadow: 0 0 12px #00eaff, 0 0 30px #7b2cff;
}

.subtitle {
    text-align: center;
    color: #dce7ff;
    font-size: 18px;
    margin-bottom: 25px;
}

.card {
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 24px;
    padding: 24px;
    margin: 15px 0;
    box-shadow: 0 0 30px rgba(0,220,255,0.12);
}

.score-card {
    text-align: center;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 18px;
    padding: 12px;
    color: white;
}

.score-number {
    font-size: 30px;
    font-weight: 900;
}

.round-title {
    text-align: center;
    color: white;
    font-size: 24px;
    font-weight: 900;
    margin: 20px 0;
}

.battle-card {
    text-align: center;
    background: rgba(255,255,255,0.08);
    border: 2px solid rgba(255,255,255,0.25);
    border-radius: 28px;
    padding: 25px;
    box-shadow: 0 0 35px rgba(0,220,255,0.18);
}

.fighter-name {
    color: white;
    font-size: 22px;
    font-weight: 900;
}

.hand {
    font-size: 78px;
    display: inline-block;
    margin: 10px;
}

.shaking {
    animation: shake 0.28s infinite alternate;
}

@keyframes shake {
    from {
        transform: rotate(-18deg) translateX(-10px);
    }

    to {
        transform: rotate(18deg) translateX(10px);
    }
}

.ready {
    text-align: center;
    color: white;
    font-size: 46px;
    font-weight: 900;
    margin: 20px;
    text-shadow: 0 0 15px #00eaff;
}

.countdown {
    text-align: center;
    color: white;
    font-size: 85px;
    font-weight: 900;
    text-shadow: 0 0 25px #00eaff;
}

.boom {
    text-align: center;
    font-size: 100px;
    animation: explosion 0.5s ease-out;
}

@keyframes explosion {

    0% {
        transform: scale(0.1) rotate(-30deg);
        opacity: 0;
    }

    50% {
        transform: scale(1.6) rotate(15deg);
        opacity: 1;
    }

    100% {
        transform: scale(1) rotate(0deg);
        opacity: 1;
    }
}

.result-card {
    text-align: center;
    background: rgba(255,255,255,0.10);
    border-radius: 22px;
    padding: 25px;
    margin: 20px 0;
}

.result-title {
    color: white;
    font-size: 34px;
    font-weight: 900;
}

.result-text {
    color: #e4edff;
    font-size: 18px;
}

.final-title {
    text-align: center;
    color: white;
    font-size: 48px;
    font-weight: 900;
    text-shadow: 0 0 15px #00eaff, 0 0 35px #7b2cff;
}

.final-score {
    text-align: center;
    color: white;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.20);
    border-radius: 20px;
    padding: 20px;
}

.final-number {
    font-size: 42px;
    font-weight: 900;
}

.footer {
    text-align: center;
    color: #aab8d4;
    margin-top: 30px;
}
</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# WINNER FUNCTION
# ============================================================

def find_winner(user, computer):

    if user == computer:
        return "draw"

    if user == "rock" and computer == "scissor":
        return "user"

    if user == "paper" and computer == "rock":
        return "user"

    if user == "scissor" and computer == "paper":
        return "user"

    return "computer"


# ============================================================
# RESET GAME
# ============================================================

def reset_game():

    st.session_state.started = False

    st.session_state.round = 1

    st.session_state.user_wins = 0

    st.session_state.computer_wins = 0

    st.session_state.draws = 0

    st.session_state.user_choice = None

    st.session_state.computer_choice = None

    st.session_state.battle_started = False

    st.session_state.result_shown = False

    st.session_state.game_over = False


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.started:

    st.markdown(
        '<div class="game-title">'
        '🎮 ADITYA\'S GAMES WORLD 🎮'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        '⚡ HUMAN VS MACHINE ⚡'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card">'
        '<h2 style="text-align:center;color:white;">'
        '🪨 📄 ✂️ ROCK PAPER SCISSOR'
        '</h2>'

        '<p style="color:#e5edff;font-size:18px;">'
        'Welcome challenger! Prepare yourself for '
        '<strong>10 rounds</strong> against the computer.'
        '</p>'

        '<h3 style="color:white;">📜 RULES</h3>'

        '<p style="color:#dce7ff;font-size:17px;">'
        '🪨 Rock beats ✂️ Scissor<br>'
        '📄 Paper beats 🪨 Rock<br>'
        '✂️ Scissor beats 📄 Paper<br>'
        '🤝 Same choice = Draw'
        '</p>'

        '<h3 style="color:white;">🏆 HOW TO WIN</h3>'

        '<p style="color:#dce7ff;font-size:17px;">'
        'Choose your weapon. The computer will secretly '
        'choose its weapon after you. After 10 rounds, '
        'the player with the most victories wins!'
        '</p>'

        '<h3 style="color:white;">🎹 GAME ATMOSPHERE</h3>'

        '<p style="color:#dce7ff;font-size:17px;">'
        '🎹 Cinematic piano music while you play<br>'
        '🤜🤛 Shaking battle animation<br>'
        '💥 Powerful boom after the showdown<br>'
        '🎈 Celebration at the end'
        '</p>'

        '</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "🚀 ENTER ADITYA'S GAMES WORLD",
        use_container_width=True
    ):

        st.session_state.started = True

        st.rerun()

    st.markdown(
        '<div class="footer">'
        '🐍 Built with Python + Streamlit ❤️'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# GAME SCREEN
# ============================================================

elif not st.session_state.game_over:

    # --------------------------------------------------------
    # PIANO LOOP
    # --------------------------------------------------------

    st.markdown(
        '<audio autoplay loop style="display:none;">'
        '<source src="data:audio/wav;base64,'
        + PIANO_BASE64
        + '" type="audio/wav">'
        '</audio>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="game-title">'
        '🎮 ADITYA\'S GAMES WORLD'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="score-card">'
            '😎 YOU<br>'
            '<span class="score-number">'
            + str(st.session_state.user_wins)
            + '</span>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            '<div class="score-card">'
            '🤖 COMPUTER<br>'
            '<span class="score-number">'
            + str(st.session_state.computer_wins)
            + '</span>'
            '</div>',
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            '<div class="score-card">'
            '🤝 DRAW<br>'
            '<span class="score-number">'
            + str(st.session_state.draws)
            + '</span>'
            '</div>',
            unsafe_allow_html=True
        )


    st.markdown(
        '<div class="round-title">'
        'ROUND '
        + str(st.session_state.round)
        + ' / '
        + str(TOTAL_ROUNDS)
        + '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # CHOOSE WEAPON
    # ========================================================

    if not st.session_state.battle_started:

        st.markdown(
            '<div style="text-align:center;'
            'font-size:28px;'
            'font-weight:900;'
            'color:white;'
            'margin-bottom:20px;">'
            '⚔️ CHOOSE YOUR WEAPON ⚔️'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                "🪨 ROCK",
                use_container_width=True
            ):

                st.session_state.user_choice = "rock"

                st.session_state.computer_choice = random.choice(
                    list(WEAPONS.keys())
                )

                st.session_state.battle_started = True

                st.session_state.result_shown = False

                st.rerun()


        with col2:

            if st.button(
                "📄 PAPER",
                use_container_width=True
            ):

                st.session_state.user_choice = "paper"

                st.session_state.computer_choice = random.choice(
                    list(WEAPONS.keys())
                )

                st.session_state.battle_started = True

                st.session_state.result_shown = False

                st.rerun()


        with col3:

            if st.button(
                "✂️ SCISSOR",
                use_container_width=True
            ):

                st.session_state.user_choice = "scissor"

                st.session_state.computer_choice = random.choice(
                    list(WEAPONS.keys())
                )

                st.session_state.battle_started = True

                st.session_state.result_shown = False

                st.rerun()


    # ========================================================
    # BATTLE
    # ========================================================

    else:

        # ----------------------------------------------------
        # BATTLE DISPLAY
        # ----------------------------------------------------

        st.markdown(
            '<div class="battle-card">'
            '<div class="fighter-name">😎 YOU</div>'
            '<div class="hand shaking">🤜</div>'
            '<div style="color:white;font-size:30px;font-weight:900;">VS</div>'
            '<div class="fighter-name">🤖 COMPUTER</div>'
            '<div class="hand shaking">🤛</div>'
            '</div>',
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # RUN BATTLE ONLY ONCE
        # ----------------------------------------------------

        if not st.session_state.result_shown:

            st.markdown(
                '<div class="ready">READY?</div>',
                unsafe_allow_html=True
            )

            time.sleep(0.6)

            countdown = st.empty()

            for number in [3, 2, 1]:

                countdown.markdown(
                    '<div class="countdown">'
                    + str(number)
                    + '</div>',
                    unsafe_allow_html=True
                )

                time.sleep(0.65)

            countdown.empty()


            # ------------------------------------------------
            # BOOM
            # ------------------------------------------------

            st.markdown(
                '<div class="boom">💥</div>',
                unsafe_allow_html=True
            )

            st.audio(
                BOOM_SOUND,
                format="audio/wav",
                autoplay=True
            )

            time.sleep(0.5)


            # ------------------------------------------------
            # CALCULATE RESULT
            # ------------------------------------------------

            result = find_winner(
                st.session_state.user_choice,
                st.session_state.computer_choice
            )

            if result == "user":

                st.session_state.user_wins += 1

            elif result == "computer":

                st.session_state.computer_wins += 1

            else:

                st.session_state.draws += 1


            st.session_state.result_shown = True


        # ----------------------------------------------------
        # SHOW WEAPONS
        # ----------------------------------------------------

        user_weapon = WEAPONS[
            st.session_state.user_choice
        ]

        computer_weapon = WEAPONS[
            st.session_state.computer_choice
        ]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(
                '<div style="text-align:center;">'
                '<div style="font-size:75px;">'
                + user_weapon
                + '</div>'
                '<div style="color:white;font-size:18px;font-weight:900;">'
                'YOU'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                '<div style="text-align:center;'
                'font-size:35px;'
                'font-weight:900;'
                'color:white;'
                'margin-top:30px;">'
                'VS'
                '</div>',
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                '<div style="text-align:center;">'
                '<div style="font-size:75px;">'
                + computer_weapon
                + '</div>'
                '<div style="color:white;font-size:18px;font-weight:900;">'
                'COMPUTER'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # RESULT MESSAGE
        # ----------------------------------------------------

        result = find_winner(
            st.session_state.user_choice,
            st.session_state.computer_choice
        )

        if result == "user":

            title = "🎉 YOU WIN!"

            message = (
                "🔥 BOOM! Perfect move! "
                "The computer got destroyed! 😂"
            )

        elif result == "computer":

            title = "🤖 COMPUTER WINS!"

            message = (
                "💀 The machine got you this time! "
                "REVENGE! 😤"
            )

        else:

            title = "🤝 DRAW!"

            message = (
                "😐 Both of you survived the showdown!"
            )

        st.markdown(
            '<div class="result-card">'
            '<div class="result-title">'
            + title
            + '</div>'
            '<div class="result-text">'
            + message
            + '</div>'
            '</div>',
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # NEXT ROUND
        # ----------------------------------------------------

        if st.session_state.round < TOTAL_ROUNDS:

            if st.button(
                "➡️ NEXT ROUND",
                use_container_width=True
            ):

                st.session_state.round += 1

                st.session_state.user_choice = None

                st.session_state.computer_choice = None

                st.session_state.battle_started = False

                st.session_state.result_shown = False

                st.rerun()


        else:

            if st.button(
                "🏆 SHOW FINAL RESULTS",
                use_container_width=True
            ):

                st.session_state.game_over = True

                st.rerun()


# ============================================================
# FINAL RESULTS
# ============================================================

else:

    user_score = st.session_state.user_wins

    computer_score = st.session_state.computer_wins

    draw_score = st.session_state.draws


    # --------------------------------------------------------
    # DETERMINE FINAL WINNER
    # --------------------------------------------------------

    if user_score > computer_score:

        st.balloons()

        final_title = "👑 YOU ARE THE CHAMPION!"

        final_message = (
            "🔥 10 rounds completed! "
            "You absolutely destroyed the computer! 😂"
        )

    elif computer_score > user_score:

        final_title = "🤖 COMPUTER WINS!"

        final_message = (
            "💀 The machines have taken over! "
            "Train harder for the rematch! 😂"
        )

    else:

        final_title = "🤝 EPIC DRAW!"

        final_message = (
            "😎 Neither human nor machine "
            "could claim supremacy!"
        )


    # --------------------------------------------------------
    # FINAL TITLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="final-title">'
        '🏆 GAME OVER 🏆'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="result-card">'
        '<div class="result-title">'
        + final_title
        + '</div>'
        '<div class="result-text">'
        + final_message
        + '</div>'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # FINAL SCOREBOARD
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="final-score">'
            '😎<br>'
            'YOU<br>'
            '<span class="final-number">'
            + str(user_score)
            + '</span>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            '<div class="final-score">'
            '🤖<br>'
            'COMPUTER<br>'
            '<span class="final-number">'
            + str(computer_score)
            + '</span>'
            '</div>',
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            '<div class="final-score">'
            '🤝<br>'
            'DRAWS<br>'
            '<span class="final-number">'
            + str(draw_score)
            + '</span>'
            '</div>',
            unsafe_allow_html=True
        )


    st.write("")


    # --------------------------------------------------------
    # PLAY AGAIN
    # --------------------------------------------------------

    if st.button(
        "🔄 PLAY AGAIN",
        use_container_width=True
    ):

        reset_game()

        st.rerun()


    st.markdown(
        '<div class="footer">'
        '🎮 Thanks for playing Aditya\'s Games World!'
        '</div>',
        unsafe_allow_html=True
    )