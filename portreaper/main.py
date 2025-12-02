#!/usr/bin/env python3
import click
import psutil
import sys
from nmap import PortScanner


@click.group()
@click.version_option(version="0.1.0", prog_name=click.style("PortReaper 💀", fg="red", bold=True))
def cli():
    """PortReaper 💀 — The silent harbinger for port-hogging processes."""
    pass


@cli.command()
@click.argument("host", default="127.0.0.1")
@click.option("--ports", "-p", default="1-1024", help="Port range (e.g. 1-1000 or 22,80,443)")
def scan(host, ports):
    """Scan for open ports."""
    click.echo(f"Scanning {host} → {ports}...")
    nm = PortScanner()
    try:
        nm.scan(host, ports)
    except Exception as e:
        click.echo(f"Scan failed: {e}", err=True)
        sys.exit(1)

    open_ports = []
    for h in nm.all_hosts():
        for proto in nm[h].all_protocols():
            for port in nm[h][proto]:
                if nm[h][proto][port]["state"] == "open":
                    open_ports.append(port)

    if open_ports:
        click.echo(click.style("Open ports found:", fg="red", bold=True))
        for p in sorted(open_ports):
            click.echo(f"   {p}/tcp")
    else:
        click.echo("No souls to reap. All is silent.")


@cli.command()
@click.argument("port", type=int)
def find(port):
    """Find who dares occupy this port."""
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port and conn.status == "LISTEN":
            if conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    click.echo(click.style(f"Port {port} occupied by:", fg="red", bold=True))
                    click.echo(f"   PID     : {conn.pid}")
                    click.echo(f"   Name    : {proc.name()}")
                    click.echo(f"   Command : {' '.join(proc.cmdline())}")
                except psutil.NoSuchProcess:
                    click.echo(f"Port {port} → PID {conn.pid} (already dead)")
            else:
                click.echo(f"Port {port} open (kernel-level)")
            return
    click.echo(f"Port {port} is free.")


@cli.command()
@click.argument("port", type=int)
@click.option("--force", "-9", is_flag=True, help="No mercy — SIGKILL")
def kill(port, force):
    """Reap the process on this port."""
    pid = None
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port and conn.status == "LISTEN" and conn.pid:
            pid = conn.pid
            break

    if not pid:
        click.echo(f"Nothing to reap on port {port}")
        return

    try:
        proc = psutil.Process(pid)
        if force:
            proc.kill()
            action = "reaped with extreme prejudice"
        else:
            proc.terminate()
            action = "sent to the void"
        click.echo(click.style(f"Process {proc.name()} (PID {pid}) {action} on port {port}", fg="red"))
    except psutil.AccessDenied:
        click.echo("Permission denied. Run with sudo.")
    except psutil.NoSuchProcess:
        click.echo("Process already gone.")


@cli.command()
@click.option("--interval", "-i", default=2, type=int, help="Refresh interval in seconds")
def monitor(interval):
    """Watch. Wait. Reap."""
    click.echo(click.style("PortReaper is watching the shadows... (Ctrl+C to vanish)", bold=True, fg="red"))
    try:
        while True:
            click.clear()
            click.echo(click.style("Listening Ports", bold=True, underline=True, fg="red"))
            ports = {}
            for conn in psutil.net_connections(kind="inet"):
                if conn.status == "LISTEN":
                    ports[conn.laddr.port] = conn.pid or "kernel"

            if not ports:
                click.echo("   All is silent...")
            else:
                for port in sorted(ports):
                    pid = ports[port]
                    try:
                        name = psutil.Process(pid).name() if pid != "kernel" else "system"
                    except:
                        name = "[gone]"
                    click.echo(f"   {port:5d} → {name}")
            click.echo(f"\nRefresh every {interval}s | Ctrl+C to stop")
            import time; time.sleep(interval)
    except KeyboardInterrupt:
        click.echo(click.style("\nThe reaper fades into the mist...", fg="red"))


if __name__ == "__main__":
    cli()