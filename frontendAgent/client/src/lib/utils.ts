import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import dayjs from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

dayjs.extend(localizedFormat);

export const moment = dayjs;

export const formatAgentName = (name: string) => {
    return name.substring(0, 2);
};

export const formatLargeNumber = (num: number): string => {
    if (num >= 1e9) {
        return `$${(num / 1e9).toFixed(2)}B`;
    }
    if (num >= 1e6) {
        return `$${(num / 1e6).toFixed(2)}M`;
    }
    if (num >= 1e3) {
        return `$${(num / 1e3).toFixed(2)}K`;
    }
    return `$${num.toFixed(2)}`;
};
