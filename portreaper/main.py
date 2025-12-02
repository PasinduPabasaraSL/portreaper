#!/usr/bin/env python3
import click
import psutil
from nmap import PortScanner
import sys

@click.group()
@click.version_option(version="0.1.0", prog_name="PortReaper")
def cli():
    """PortReaper 💀 — The silent harbinger for port-hogging processes."""
    pass

@cli.command()
@click.argument('host', default='127.0.0.1')
@click.option('--ports', '-p', default='1-1024', help='Ports/range to scan')
def scan(host, ports):
    """Scan for open ports."""
    click.echo(f"🔍 Scanning {host} ({ports})...")
    nm = PortScanner()
    try:
        result = nm.scan(host, ports)
    except Exception as e:
        click.echo(f"Scan failed: {e}", err=True)
        sys.exit(1)

    open_ports = []
    for h in nm.all_hosts():
        for proto in nm[h].all_protocols():
            for port in nm[h][proto]:
                if nm[h][proto][port]['state'] == 'open':
                    open_ports.append(port)

    if open_ports:
        click.echo(click.style("💀 Open ports found:", fg="red", bold=True))
        for p in sorted(open_ports):
            click.echo(f"   {p}/tcp")
    else:
        click.echo("No open ports. All is quiet... for now.")

@cli.command()
@click.argument('port', type=int)
def find(port):
    """Find who dares occupy this port."""
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port and conn.status == 'LISTEN':
            if conn.pid:
                proc = psutil.Process(conn.pid)
                click.echo(click.style(f"💀 Port {port} occupied by:", bold=True))
                click.echo(f"   PID     : {conn.pid}")
                click.echo(f"   Process : {proc.name()}")
                click.echo(f"   Command : {' '.join(proc.cmdline())}")
            else:
                click.echo(f"💀 Port {port} open (kernel-level)")
            return
    click.echo(f"Port {port} is free.")

@cli.command()
@click.argument('port', type=int)
@click.option('--force', '-9', is_flag=True, help="No mercy (SIGKILL)")
def kill(port, force):
    """Reap the process on this port."""
    pid = None
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port and conn.status == 'LISTEN' and conn.pid:
            pid = conn.pid
            break
    if not pid:
        click.echo(f"Nothing to reap on port {port}")
        return

    proc = psutil.Process(pid)
    proc.terminate() if not force else proc.kill()
    action = "reaped with extreme prejudice" if force else "sent to the void"
    click.echo(click.style(f"💀 Process {proc.name()} (PID {pid}) {action} on port {port}", fg="red"))

@cli.command()
@click.option('--interval', '-i', default=2, help='Refresh interval')
def monitor(interval):
    """Watch. Wait. Reap."""
    click.echo(click.style("💀 PortReaper is watching... (Ctrl+C to stop)", bold=True))
    try:
        while True:
            click.clear()
            click.echo(click.style("Listening Ports", bold=True, underline=True))
            ports = {}
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN' and conn.laddr.port:
                    ports[conn.laddr.port] = conn.pid or "kernel"
            if not ports:
                click.echo("  All is silent...")
            else:
                for port in sorted(ports):
                    pid = ports[port]
                    name = psutil.Process(pid).name() if pid != "kernel" else "system"
                    click.echo(f"  {port:5d} → {name}")
            click.echo(f"\nRefresh: {interval}s | Ctrl+C to vanish")
            import time; time.sleep(interval)
    except KeyboardInterrupt:
        click.echo(click.style("\n💀 The reaper fades into the shadows...", fg="red"))

if __name__ == '__main__':
    cli()
