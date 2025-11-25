-- ============================================
-- AH Scanner - Scanner d'hôtel des ventes
-- ============================================

-- https://warcraft.wiki.gg/wiki/API_GetAuctionItemInfo

-- Initialisation de la base de données
AHScannerDB = AHScannerDB or {
    scans = {},
    settings = {
        autoScan = false,
        scanDelay = 0.5
    }
}

-- Variables locales
local AHScanner = CreateFrame("Frame")
local currentScan = {}
local isScanning = false
local currentPage = 0
local totalPages = 0
local scanStartTime = 0
local currentItemIndex = 1
local itemsToScan = {"Copper Ore", "Copper Bar",
"Tin Ore", "Tin Bar",
"Iron Ore", "Iron Bar",
"Silver Ore", "Silver Bar",
"Truesilver Ore", "Truesilver Bar",
"Gold Ore", "Gold Bar",
"Mithril Ore", "Mithril Bar"}

-- ============================================
-- Fonctions utilitaires
-- ============================================

local function Print(msg)
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[AH Scanner]|r " .. msg)
end

local function FormatPrice(copper)
    if not copper or copper == 0 then return "0c" end
    local gold = math.floor(copper / 10000)
    local silver = math.floor((copper % 10000) / 100)
    local c = copper % 100
    
    local str = ""
    if gold > 0 then str = str .. gold .. "g " end
    if silver > 0 then str = str .. silver .. "s " end
    if c > 0 or str == "" then str = str .. c .. "c" end
    return str
end


-- ============================================
-- Fonctions de scan
-- ============================================

function AHScanner:StartScan()
    -- Vérifier qu'on est à l'AH
    if not AuctionFrame or not AuctionFrame:IsShown() then
        Print("Tu dois être à l'hôtel des ventes pour scanner!")
        return
    end
    
    if isScanning then
        Print("Un scan est déjà en cours...")
        return
    end
    
    -- Vérifier qu'il y a des données
    local canQuery, canQueryAll = CanSendAuctionQuery()
    if not canQuery then
        Print("ERREUR: Impossible de lancer une requête AH maintenant")
        Print("Attends quelques secondes et réessaie")
        return
    end
    
    -- Initialiser le scan
    isScanning = true
    currentScan = {
        items = {},
        startTime = time(),
        totalItems = 0,
    }
    currentPage = 0
    scanStartTime = GetTime()
    
    Print("Début du scan de l'hôtel des ventes...")
    Print("Scanning: " .. itemsToScan[1] .. " et " .. itemsToScan[2])
    
    -- Initialiser le scan du premier item
    currentItemIndex = 1
    currentPage = 0
    
    Print("Scan de " .. itemsToScan[currentItemIndex] .. "...")
    QueryAuctionItems(itemsToScan[currentItemIndex], nil, nil, 0, 0, 0, 0)
    
    -- Timeout de sécurité
    C_Timer.After(10, function()
        if isScanning and currentPage == 0 then
            Print("TIMEOUT: Aucune réponse de l'AH. Réessaie.")
            isScanning = false
        end
    end)
end

function AHScanner:ProcessPage()
    local numBatchAuctions, totalAuctions = GetNumAuctionItems("list")
    
    Print(string.format("ProcessPage appelé: numBatch=%d, total=%d", numBatchAuctions, totalAuctions))
    
    -- Si pas de données mais qu'on sait qu'il y en a, on réessaie
    if numBatchAuctions == 0 and totalAuctions > 0 then
        Print("Données pas encore chargées " .. itemsToScan[currentItemIndex] .. " " .. currentPage, " on réessaie dans 2s...")
        C_Timer.After(2, function()
            self:ProcessPage()
        end)
        return
    end
    
    if numBatchAuctions == 0 and totalAuctions == 0 then
        Print("ERREUR: Aucune donnée dans l'AH")
        self:FinishScan()
        return
    end
    
    if numBatchAuctions == 0 then
        self:FinishScan()
        return
    end

    -- Parcourir toutes les enchères de la page
    local itemsFound = 0
    local itemsWithIncompleteInfo = 0
    
    for i = 1, numBatchAuctions do
        local name, _, count, quality, _, level, minBid, minIncrement,
              buyout, bidAmount, highBidder, seller = 
              GetAuctionItemInfo("list", i)
        
        -- On n'utilise plus itemId car il n'est pas dispo sur Ascension
        if name then
            -- Vérifier que c'est bien l'item qu'on scanne actuellement
            if name == itemsToScan[currentItemIndex] then
                -- Si hasAllInfo est false, les informations ne sont pas encore complètes
                -- (l'objet n'est pas encore dans le cache local)
                itemsFound = itemsFound + 1
                -- Créer ou mettre à jour l'entrée pour cet item (utilise le nom comme clé)
                local itemKey = name .. "_" .. currentPage .. "_" .. i
                if not currentScan.items[itemKey] then
                    currentScan.items[itemKey] = {
                        name = name,
                        count = count,
                        quality = quality,
                        level = level,
                        minBid = minBid,
                        minIncrement = minIncrement,
                        buyout = buyout,
                        buyoutUnit = buyout / count,
                        minBidUnit = minBid / count,
                        bidAmount = bidAmount,
                        highBidder = highBidder,
                        seller = (seller and seller ~= "") and seller or "Unknown",
                    }
                end
            end
        end
    end

    -- Calculer le nombre total de pages
    totalPages = math.ceil(totalAuctions / 50)
    currentPage = currentPage + 1
    
    Print(string.format("Page %d/%d scannée pour %s (%d items au total)", 
          currentPage, totalPages, itemsToScan[currentItemIndex], currentScan.totalItems))
    
    -- Scanner la page suivante si nécessaire pour l'item actuel
    if currentPage < totalPages then
        C_Timer.After(AHScannerDB.settings.scanDelay, function()
            QueryAuctionItems(itemsToScan[currentItemIndex], nil, nil, 0, 0, 0, currentPage)
        end)
    else
        -- Fin du scan pour cet item, passer au suivant
        currentItemIndex = currentItemIndex + 1
        if currentItemIndex <= #itemsToScan then
            -- Scanner le prochain item
            currentPage = 0
            Print("Scan de " .. itemsToScan[currentItemIndex] .. "...")
            C_Timer.After(AHScannerDB.settings.scanDelay, function()
                QueryAuctionItems(itemsToScan[currentItemIndex], nil, nil, 0, 0, 0, 0)
            end)
        else
            -- Tous les items ont été scannés
            self:FinishScan()
        end
    end
end

function AHScanner:FinishScan()
    isScanning = false
    currentScan.endTime = time()
    currentScan.duration = GetTime() - scanStartTime
    
    local realm = GetRealmName() or "Unknown"
    
    -- Initialiser le realm s'il n'existe pas
    if not AHScannerDB[realm] then
        AHScannerDB[realm] = {}
    end
    
    -- Grouper les items par nom
    local itemsByName = {}
    for _, item in pairs(currentScan.items) do
        local itemName = item.name
        if not itemsByName[itemName] then
            itemsByName[itemName] = {}
        end
        table.insert(itemsByName[itemName], item)
    end
    
    -- Sauvegarder les items par nom sous le realm
    for itemName, items in pairs(itemsByName) do
        if not AHScannerDB[realm][itemName] then
            AHScannerDB[realm][itemName] = {}
        end
        if not AHScannerDB[realm][itemName]["items"] then
            AHScannerDB[realm][itemName]["items"] = {}
        end
        -- Ajouter les items au tableau existant
        for _, item in ipairs(items) do
            table.insert(AHScannerDB[realm][itemName]["items"], item)
        end
    end
    
    -- Convertir la table en array pour faciliter l'export (garder pour compatibilité)
    local itemsArray = {}
    for _, item in pairs(currentScan.items) do
        table.insert(itemsArray, item)
    end
    currentScan.items = itemsArray
    
    -- Sauvegarder aussi dans scans pour compatibilité
    if not AHScannerDB.scans then
        AHScannerDB.scans = {}
    end
    table.insert(AHScannerDB.scans, currentScan)
    
    -- Limiter à 10 scans maximum
    if #AHScannerDB.scans > 10 then
        table.remove(AHScannerDB.scans, 1)
    end
    
    Print(string.format("Scan terminé! %d items uniques trouvés en %.1f secondes", 
          #currentScan.items, currentScan.duration))
    Print("Les données sont sauvegardées dans AHScannerDB")
end

function AHScanner:StopScan()
    if not isScanning then
        Print("Aucun scan en cours")
        return
    end
    isScanning = false
    Print("Scan arrêté")
end

-- ============================================
-- Fonctions d'affichage
-- ============================================

function AHScanner:ShowLastScan()
    if #AHScannerDB.scans == 0 then
        Print("Aucun scan disponible")
        return
    end
    
    local scan = AHScannerDB.scans[#AHScannerDB.scans]
    Print(string.format("Dernier scan: %s", date("%Y-%m-%d %H:%M:%S", scan.startTime)))
    Print(string.format("Durée: %.1f secondes", scan.duration))
    Print(string.format("Items trouvés: %d", #scan.items))
    Print("---")
    
    -- Afficher les 10 premiers items
    Print("Aperçu des items (10 premiers):")
    for i, item in ipairs(scan.items) do
        Print(string.format("  %s x%d - Min: %s, Price: %s, Who: %s",
              item.name, item.count, 
              FormatPrice(item.minBid), 
              FormatPrice(item.buyoutPrice),
              item.owner))
    end
    
    if #scan.items > 10 then
        Print(string.format("  ... et %d autres items", #scan.items - 10))
    end
end

function AHScanner:ExportToChat()
    if #AHScannerDB.scans == 0 then
        Print("Aucun scan à exporter")
        return
    end
    
    local scan = AHScannerDB.scans[#AHScannerDB.scans]
    Print("Export JSON (copie depuis la console):")
    Print("---")
    
    local json = "{"
    json = json .. '"timestamp":' .. scan.startTime .. ','
    json = json .. '"duration":' .. scan.duration .. ','
    json = json .. '"items":['
    
    for i, item in ipairs(scan.items) do
        if i > 1 then json = json .. "," end
        json = json .. string.format('{"name":"%s","count":%d,"min":%d,"max":%d,"stock":%d}',
                                     item.name, item.count, 
                                     item.minPrice, item.maxPrice, item.totalStock)
    end
    
    json = json .. "]}"
    
    Print(json)
end

function AHScanner:ClearData()
    AHScannerDB.scans = {}
    Print("Toutes les données ont été effacées")
end

-- ============================================
-- Gestion des événements
-- ============================================

AHScanner:RegisterEvent("AUCTION_ITEM_LIST_UPDATE")
AHScanner:RegisterEvent("ADDON_LOADED")

AHScanner:SetScript("OnEvent", function(self, event, ...)
    if event == "ADDON_LOADED" then
        local addonName = ...
        if addonName == "AHScanner" then
            Print("Chargé! Tape /ahscan pour voir les commandes")
        end
    elseif event == "AUCTION_ITEM_LIST_UPDATE" then
        if isScanning then
            self:ProcessPage()
        end
    end
end)

-- ============================================
-- Commandes slash
-- ============================================

SLASH_AHSCANNER1 = "/ahscan"
SLASH_AHSCANNER2 = "/ahs"

SlashCmdList["AHSCANNER"] = function(msg)
    msg = string.lower(msg or "")
    
    if msg == "start" or msg == "scan" then
        AHScanner:StartScan()
    elseif msg == "stop" then
        AHScanner:StopScan()
    elseif msg == "show" or msg == "last" then
        AHScanner:ShowLastScan()
    elseif msg == "export" then
        AHScanner:ExportToChat()
    elseif msg == "clear" then
        AHScanner:ClearData()
    else
        Print("Commandes disponibles:")
        Print("  /ahscan start - Démarre un scan")
        Print("  /ahscan stop - Arrête le scan en cours")
        Print("  /ahscan show - Affiche le dernier scan")
        Print("  /ahscan export - Export JSON dans le chat")
        Print("  /ahscan clear - Efface toutes les données")
        Print("")
        Print("Les données sont sauvegardées dans:")
        Print("WTF/Account/[COMPTE]/SavedVariables/AHScanner.lua")
    end
end

Print("Tapez /ahscan pour voir les commandes disponibles")