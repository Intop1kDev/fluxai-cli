import os
import subprocess
import time
import random
import requests
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live

load_dotenv()

console = Console()

api_key = os.getenv("API_KEY")

settings = {
    "temperature": 1,
    "model": "deepseek-ai/deepseek-v3.1-terminus",
    "prompt": "Ты ИИ-ассистент FluxAI."
}

messages = [{
    "role": "system", "content": settings["prompt"]
}]

client = OpenAI(base_url="https://ai.megallm.io/v1", api_key=api_key)

console.print(Panel(f"FluxAI-cli, [bold cyan]{settings.get("model")}[/bold cyan] [bold white]/help to help.[/bold white]", border_style="green", title="Info"))

def main():
    while True:
        q = console.input("[bold yellow]USER: [/bold yellow]")

        if q.lower() == "/help":
            console.print(f"\n[bold green]/get_database[/bold green] - показывает вашу историю\n[bold green]/info[/bold green] - выводит информацию о сессии\n[bold green]/modify[/bold green] - Позволяет менять настройки\n[bold green]/clear[/bold green] - очищает чат\n")
            continue
        elif q.lower() == "/get_database":
            print(messages)
            continue
        elif q.lower() == "/info":
            console.print(f"\n[bold green]FluxAI-cli V1[/bold green]:\n[bold yellow]temperature={settings.get("temperature")}[/bold yellow]\nmodel={settings.get("model")}\n[bold yellow]prompt={settings.get("prompt")}[/bold yellow]\n")
            continue
        elif q.lower() == "/quit" or q == "/exit" or q == "/leave":
            exit()
        elif q.lower() == "/modify":
            rawtemp = console.input(f"\nEnter temperature ([bold cyan]{settings.get("temperature")}[/bold cyan]): ")
            
            if not rawtemp.strip(): # Если ввели пустоту или пробелы
                console.print("[yellow]Aborted.[/yellow]\n")
                continue
                
            try:
                mtemp = float(rawtemp)
                if 0 <= mtemp <= 2: # Температура обычно от 0 до 2
                    settings["temperature"] = mtemp
                    console.print(f"\n[bold blue]OK.[/bold blue]\n")
                else:
                    console.print("\n[bold red]ERROR[/bold red]: Temperature must be between 0 and 2\n")
            except ValueError:
                console.print("\n[bold red]ERROR[/bold red]: Please enter a valid number\n")
            rawprompt = console.input(f"Enter new prompt: ")
            if not rawprompt.strip():
                console.print("\n[bold red]ERROR[/bold red]: Please enter a valid prompt\n")
            else:
                console.print(f"\n[bold blue]OK.[/bold blue]\n")
                messages[0]["content"] = rawprompt
                settings.update(prompt=rawprompt)
                continue
            
                
                
            continue
        elif q.lower() == "/clear":
            messages.clear()
            messages.append({"role": "system", "content": settings.get("prompt")})
            console.print(f"[bold green]OK.[/bold green]")
            continue
        
        else:
            pass

        print()

        messages.append({"role": "user", "content": q})

        full_resp = ""

        console.print(f"[bold green]Flux: [/bold green]")

        with Live(Markdown(""), console=console, refresh_per_second=10, vertical_overflow="visible") as live:

            try:
                resp = client.chat.completions.create(model=settings.get("model"),messages=messages,stream=True, temperature=settings.get("temperature"))

                for chunk in resp:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_resp += content
                        live.update(Markdown(f"{full_resp}"))
            except Exception as e:
                console.print(f"[bold red]ERROR[/bold red]: {e}")
        
        print()

        # anws = resp.choices[0].message.content.strip()
        # console.print(f"[bold green]Flux: [/bold green]")
        # console.print(Markdown(f"{anws}\n"))
        messages.append({"role": "assistant", "content": full_resp})

if __name__ == "__main__":
    main()