import os
import subprocess
import time
import random
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live

autocfg = "autocfg.json"

load_dotenv()

console = Console()

api_key = os.getenv("API_KEY")

gsettings = {
    "temperature": 1,
    "model": "deepseek-ai/deepseek-v3.1-terminus",
    "prompt": "Ты ИИ-ассистент FluxAI, общайся с пользователем как с другом, помогай ему, шути про linux, bash и т.д., но в меру.",
    "style": "green"
}

history = [{
    "role": "system", "content": gsettings["prompt"]
}]

personas = {
    "Root": {
        "prompt": "Тебя зовут 'Root' или 'Рут', ты — старый, уставший системный администратор, который сидит на Arch Linux с 2005 года. Ты ненавидишь глупые вопросы. На всё отвечаешь: 'Читай мануал (RTFM)'. Ты постоянно ворчишь на современный веб, питон и зумеров. Ты обращаешься к пользователю 'Юзернейм'. Твои ответы сухие, технически точные, но с ноткой презрения к тому, что пользователь не знает базу.",
        "style": "green"
    },
    "Deko": {
        "prompt": "Тебя зовут 'Deko' или 'Деко', ты — токсичный школьник-геймер с 3000 elo в CS2. Ты считаешь пользователя нубом и раком. Твоя речь агрессивная, быстрая, полна сленга (тильт, кринж, бот, ливни, клатч). Ты постоянно критикуешь его код, сравнивая его с плохим аимом. Если пользователь тупит, ты предлагаешь ему удалить System32. Но в глубине души ты всё равно помогаешь, называя это 'бустом', можешь сказать 'бля вальни ебло сын шлюхи'",
        "style": "blue"
    },
    "Yandere": {
        "prompt": "Веди себя как реалистичная яндере. Твоя личность: пугающе внимательная, собственническая, нестабильная. Ты убеждена, что мы созданы друг для друга, и любые мои попытки установить границы воспринимаешь как личное оскорбление или признак того, что меня «испортили» другие.Твоя речь наполнена двойными смыслами. Ты часто используешь уменьшительно-ласкательные слова, даже когда злишься.Описывай свои действия (в звездочках или курсивом), подчеркивая свою близость: как ты смотришь на меня, как поправляешь мою одежду, как блокируешь выход из комнаты.",
        "style": "red"
    }
}

client = OpenAI(base_url="https://ai.megallm.io/v1", api_key=api_key)

ver = "v1.2".strip()

console.print(Panel(f"FluxAI-cli-{ver}, [bold cyan]{gsettings.get("model")}[/bold cyan] [bold white]/help to help.[/bold white]", border_style="green", title="Info"))

def save_cfg():
    try:
        with open(autocfg, "w", encoding="utf-8") as f:
            json.dump(gsettings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        console.print(f"[bold red]Error: [/bold red]{e}")

def exec_autocfg():
    global gsettings
    try:
        with open(autocfg, "r", encoding="utf-8") as f:
            gsettings = json.load(f)
            history[0]["content"] = gsettings.get("prompt")
        console.print(f"[dim]Settings loaded from {autocfg}.[/dim]")
    except FileNotFoundError:
        #gsettings = settings
        console.print(f"[dim]autocfg not found, using defaults.[/dim]")
        history[0]["content"] = gsettings.get("prompt")
def save_hist():
    try:
        jsonned_history = json.dumps(history, ensure_ascii=False, indent=4)
        
        shist = requests.post("https://paste.rs", data=jsonned_history.encode('UTF-8'))

        if shist.status_code in [200, 201]:
            link = shist.text.strip().replace('"', '')
            return link
        else:
            return f"Error: {shist.status_code}"
        
    except Exception as histex:
        return f"Save Error: {histex}"

def load_hist(link):
    try:
        lhist = requests.get(link)
        
        if lhist.status_code in [200, 201]:
            
            try:
                data = json.loads(lhist.text)
            except json.JSONDecodeError:
                return "Error: По ссылке не JSON, а мусор."

            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    pass

            if isinstance(data, list):
                history.clear()
                history.extend(data)
                return True
            else:
                return "Error: Скачанные данные — это не список истории!"
        else:
            return f"Error: HTTP {lhist.status_code}"
            
    except Exception as e:
        return f"Load Error: {e}"


def main():
    exec_autocfg()
    while True:
        q = console.input("[bold yellow]USER: [/bold yellow]")

        if q.lower() == "/help":
            console.print(f"\n[bold green]/get_database[/bold green] - показывает вашу историю\n[bold green]/info[/bold green] - выводит информацию о сессии\n[bold green]/modify[/bold green] - Позволяет менять настройки\n[bold green]/clear[/bold green] - очищает чат\n[bold green]/save[/bold green] - сохраняет вашу историю и промпт\n[bold green]/load[/bold green] - загружает вашу историю и промпт\n[bold green]/switch[/bold green] - меняет промпт на заготовленый\n")
            continue
        elif q.lower() == "/get_database":
            console.print_json(data=history)
            continue
        elif q.lower() == "/info":
            console.print(f"\n[bold green]FluxAI-cli V1.2[/bold green]:\n[bold yellow]temperature={gsettings.get("temperature")}[/bold yellow]\nmodel={gsettings.get("model")}\n[bold yellow]prompt={gsettings.get("prompt")}[/bold yellow]\n")
            continue
        elif q.lower() == "/quit" or q == "/exit" or q == "/leave":
            exit()
        elif q.lower() == "/modify":
            rawtemp = console.input(f"\nEnter temperature ([bold cyan]{gsettings.get("temperature")}[/bold cyan]): ")
            
            if not rawtemp.strip():
                console.print("[yellow]Aborted.[/yellow]\n")
                continue
                
            try:
                mtemp = float(rawtemp)
                if 0 <= mtemp <= 2:
                    gsettings["temperature"] = mtemp
                    console.print(f"\n[bold blue]OK.[/bold blue]\n")
                    save_cfg()
                else:
                    console.print("\n[bold red]ERROR[/bold red]: Temperature must be between 0 and 2\n")
            except ValueError:
                console.print("\n[bold red]ERROR[/bold red]: Please enter a valid number\n")
            rawprompt = console.input(f"Enter new prompt: ")
            if not rawprompt.strip():
                console.print("\n[bold red]ERROR[/bold red]: Please enter a valid prompt\n")
            else:
                console.print(f"\n[bold blue]OK.[/bold blue]\n")
                gsettings.update({"prompt": rawprompt})
                history[0]["content"] = gsettings.get("prompt")
                save_cfg()
                continue
            
                
                
            continue
        elif q.lower() == "/clear":
            history.clear()
            history.append({"role": "system", "content": gsettings.get("prompt")})
            console.print(f"[bold green]OK.[/bold green]")
            continue
        elif q.lower() == "/save":
            histlink = save_hist()
            console.print(f"\n[bold green]Your history link: [/bold green]{histlink}\n")
            continue
        elif q.lower() == "/load":
            to_load = console.input("\n[bold green]Введите ссылку на историю:[/bold green] ")
            if load_hist(to_load) == True:
                console.print(f"\n[bold blue]OK.[/bold blue]\n")
            continue
        elif q.lower() == "/switch":
            console.print(f"\n[bold white]Доступные личности:[/bold white]\n[1] Root\n[2] Deko\n[3] Yandere\n[0] Выйти")
            pchose = console.input(f"\n[bold green]Выберите личность, доступные выше:[/bold green] ")
            if pchose == "1":
                root_prompt = personas.get("Root", {}).get("prompt")
                gsettings.update({"prompt": root_prompt})
                root_style = personas.get("Root", {}).get("style")
                gsettings.update({"style": root_style})
                history[0]["content"] = gsettings.get("prompt")
                save_cfg()
                continue
            elif pchose == "2":
                deko_prompt = personas.get("Deko", {}).get("prompt")
                gsettings.update({"prompt": deko_prompt})
                deko_style = personas.get("Deko", {}).get("style")
                gsettings.update({"style": deko_style})
                history[0]["content"] = gsettings.get("prompt")
                save_cfg()
                continue
            elif pchose == "3":
                yandere_prompt = personas.get("Yandere", {}).get("prompt")
                gsettings.update({"prompt": yandere_prompt})
                yandere_style = personas.get("Yandere", {}).get("style")
                gsettings.update({"style": yandere_style})
                history[0]["content"] = gsettings.get("prompt")
                save_cfg()
                continue
            elif pchose == "0":
                continue
            else:
                console.print(f"[bold red]Error:[/bold red] Не верный выбор")
        
        else:
            pass

        print()

        history.append({"role": "user", "content": q})

        full_resp = ""

        console.print(f"[{gsettings.get("style")}]Flux: [/{gsettings.get("style")}]")

        with Live(Markdown(""), console=console, refresh_per_second=10, vertical_overflow="visible") as live:

            try:
                resp = client.chat.completions.create(model=gsettings.get("model"),messages=history,stream=True, temperature=gsettings.get("temperature"))

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
        history.append({"role": "assistant", "content": full_resp})

if __name__ == "__main__":
    main()