import importlib.metadata
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk

from pip._vendor.packaging.requirements import InvalidRequirement, Requirement


PROJECT_DIR = Path(__file__).resolve().parent
APP_PATH = PROJECT_DIR / "streamlit_app.py"
os.chdir(PROJECT_DIR)


def stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    if sys.platform == "win32":
        process.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        process.send_signal(signal.SIGINT)

    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait()


def unmet_requirements() -> list[str]:
    try:
        requirement_lines = (PROJECT_DIR / "requirements.txt").read_text(
            encoding="utf-8"
        ).splitlines()
    except OSError as error:
        raise RuntimeError(f"requirements.txt를 읽을 수 없습니다: {error}") from error

    missing = []
    for line_number, raw_line in enumerate(requirement_lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            requirement = Requirement(line)
        except InvalidRequirement as error:
            raise RuntimeError(
                f"requirements.txt의 {line_number}번째 줄을 해석할 수 없습니다: {line}"
            ) from error

        if requirement.marker and not requirement.marker.evaluate():
            continue

        try:
            installed_version = importlib.metadata.version(requirement.name)
        except importlib.metadata.PackageNotFoundError:
            missing.append(f"{requirement.name}: 설치되지 않음")
            continue

        if not requirement.specifier.contains(installed_version, prereleases=True):
            missing.append(
                f"{requirement.name}: 설치된 버전 {installed_version}, "
                f"요구 버전 {requirement.specifier}"
            )

    return missing


def run_setup_command(
    command: list[str], events: queue.Queue[tuple[str, str]]
) -> int:
    events.put(("log", f"> {' '.join(command)}"))
    try:
        process = subprocess.Popen(
            command,
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
        )
    except OSError as error:
        events.put(("log", f"명령 실행 오류: {error}"))
        return 1

    if process.stdout is not None:
        for output_line in process.stdout:
            events.put(("log", output_line.rstrip()))
    return process.wait()


def prepare_environment() -> int:
    events: queue.Queue[tuple[str, str]] = queue.Queue()
    try:
        missing = unmet_requirements()
    except RuntimeError as error:
        missing = []
        startup_error = str(error)
    else:
        startup_error = ""

    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(f"시작 확인 창을 열 수 없습니다: {error}", file=sys.stderr)
        return 1

    root.title("Tesla 주가 분석 - 시작 확인")
    root.geometry("620x440")
    root.minsize(520, 360)

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="실행 환경 확인", font=("", 13, "bold")).pack(anchor="w")
    ttk.Label(frame, text=f"Python: {sys.executable}", wraplength=580).pack(
        anchor="w", pady=(8, 4)
    )

    if startup_error:
        summary = f"확인할 수 없습니다: {startup_error}"
    elif missing:
        summary = "설치가 필요하거나 requirements.txt의 버전 조건과 맞지 않습니다."
    else:
        summary = "requirements.txt의 모든 패키지 버전 조건을 만족합니다."
    status = tk.StringVar(value=summary)
    ttk.Label(frame, textvariable=status, wraplength=580).pack(anchor="w", pady=4)

    buttons = ttk.Frame(frame)
    buttons.pack(fill="x", pady=(6, 0))

    if missing:
        ttk.Label(
            frame,
            text="\n".join(f"• {item}" for item in missing),
            wraplength=580,
        ).pack(anchor="w", pady=(0, 8))

    output = tk.Text(frame, height=12, state="disabled", wrap="word")
    output.pack(fill="both", expand=True, pady=(8, 0))
    is_running = False
    result = 1 if startup_error else 2

    def append_output(text: str) -> None:
        output.configure(state="normal")
        output.insert("end", text + "\n")
        output.see("end")
        output.configure(state="disabled")

    def accept_and_close() -> None:
        nonlocal result
        result = 0
        root.destroy()

    def start() -> None:
        nonlocal is_running
        if not missing:
            accept_and_close()
            return

        is_running = True
        run_button.configure(state="disabled")
        cancel_button.configure(state="disabled")
        status.set("필요한 패키지를 설치합니다.")

        def install() -> None:
            command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(PROJECT_DIR / "requirements.txt"),
            ]
            install_code = run_setup_command(command, events)
            if install_code:
                events.put(("failed", f"패키지 설치 실패 (종료 코드 {install_code})"))
                return

            try:
                remaining = unmet_requirements()
            except RuntimeError as error:
                events.put(("failed", f"설치 후 환경을 다시 확인할 수 없습니다: {error}"))
                return
            if remaining:
                events.put(
                    (
                        "failed",
                        "설치 후에도 요구 버전을 충족하지 못했습니다: "
                        + "; ".join(remaining),
                    )
                )
                return
            events.put(("ready", "설치가 완료되었습니다. 앱을 시작합니다."))

        threading.Thread(target=install, daemon=True).start()

    run_label = "설치 후 실행" if missing else "실행"
    run_button = ttk.Button(buttons, text=run_label, command=start)
    run_button.pack(side="right")

    def cancel() -> None:
        nonlocal result
        result = 2
        root.destroy()

    cancel_button = ttk.Button(buttons, text="아니요 - 종료", command=cancel)
    cancel_button.pack(side="right", padx=(0, 8))
    if startup_error:
        run_button.configure(state="disabled")

    def close_window() -> None:
        if is_running:
            status.set("설치가 진행 중입니다. 완료될 때까지 창을 닫을 수 없습니다.")
        elif startup_error:
            root.destroy()
        else:
            cancel()

    root.protocol("WM_DELETE_WINDOW", close_window)

    def process_events() -> None:
        nonlocal is_running, result
        while True:
            try:
                event, payload = events.get_nowait()
            except queue.Empty:
                break

            if event == "log":
                append_output(payload)
            elif event == "failed":
                is_running = False
                result = 1
                status.set(payload)
                run_button.configure(text="다시 시도", state="normal")
                cancel_button.configure(text="닫기", state="normal")
            elif event == "ready":
                status.set(payload)
                accept_and_close()
                return

        root.after(100, process_events)

    root.after(100, process_events)
    root.mainloop()
    return result


def run_app() -> int:
    with tempfile.TemporaryDirectory(prefix="tesla-stock-app-") as temp_dir:
        shutdown_file = Path(temp_dir) / "shutdown.request"
        environment = {
            **os.environ,
            "TESLA_STOCK_SHUTDOWN_FILE": str(shutdown_file),
        }
        popen_options: dict[str, int] = {}
        if sys.platform == "win32":
            popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(APP_PATH)],
            cwd=PROJECT_DIR,
            env=environment,
            **popen_options,
        )

        try:
            while process.poll() is None:
                if shutdown_file.exists():
                    time.sleep(2)
                    break
                time.sleep(0.2)
        except KeyboardInterrupt:
            stop_process(process)

        if process.poll() is None:
            stop_process(process)
        return process.wait()


def main() -> int:
    setup_result = prepare_environment()
    if setup_result:
        return 0 if setup_result == 2 else setup_result
    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
