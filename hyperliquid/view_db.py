from database import TraderDatabase
import argparse

def main():
    parser = argparse.ArgumentParser(description='View Hyperliquid trader database')
    parser.add_argument('--table-info', action='store_true', help='Show table information')
    parser.add_argument('--analysis', type=int, default=5, help='Show latest analysis entries')
    parser.add_argument('--history', type=str, help='Show trading history for specific trader')
    parser.add_argument('--history-limit', type=int, default=5, help='Number of history entries to show')
    
    args = parser.parse_args()
    db = TraderDatabase()

    if args.table_info:
        db.print_table_info()
    
    if args.analysis:
        db.view_trader_analysis(limit=args.analysis)
    
    if args.history:
        db.view_trading_history(trader_address=args.history, limit=args.history_limit)
    elif args.history_limit:
        db.view_trading_history(limit=args.history_limit)

if __name__ == "__main__":
    main() 