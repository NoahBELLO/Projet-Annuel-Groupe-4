import pygame
import random

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre et de la carte
tile_size = 30
size = 20
width, height = size * tile_size, size * tile_size
interface_height = 150  # Hauteur supplémentaire pour l'interface

# Couleurs
PASSABLE_COLOR = (220, 220, 221)        # Gris clair pour les cases passables
PLAYER_COLOR = (56, 111, 164)              # Bleu pour le joueur
PLAYER_COLOR_LIGHT = (89, 165, 216)    # Bleu clair pour le joueur capable de bouger
ENEMY_COLOR = (158, 0, 89)               # Rouge bordeau pour les ennemis
ENEMY_COLOR_LIGHT = (216, 17, 89)     # Rouge pour les ennemis capables de bouger
SELECTED_COLOR = (0, 255, 0)            # Vert pour la sélection
OBJECTIVE_MAJOR_COLOR = (106, 76, 147)   # Violet pour objectif majeur
OBJECTIVE_MINOR_COLOR = (228, 160, 249)   # Violet lilas pour objectif mineur

# Classe pour les unités
class Unit:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.selected = False
        self.moved = False  # Indicateur de mouvement pour le tour
        self.pv = 2  # Points de Vie
        self.attacked_this_turn = False  # Indicateur d'attaque dans ce tour

    def draw(self, screen, units, objectives):
        """Affiche l'unité sur l'écran."""
        rect = pygame.Rect(self.x * tile_size, self.y * tile_size, tile_size, tile_size)
        if not self.moved:
            color = PLAYER_COLOR_LIGHT if self.color == PLAYER_COLOR else ENEMY_COLOR_LIGHT
        else:
            color = self.color
        pygame.draw.rect(screen, color, rect)

        if self.selected:
            pygame.draw.rect(screen, SELECTED_COLOR, rect, 3)

        font = pygame.font.SysFont(None, 16)
        symbols = self.get_symbols_on_same_tile(units)
        combined_text = font.render(symbols, True, (255, 255, 255))
        text_width = combined_text.get_width()
        text_x = self.x * tile_size + (tile_size - text_width) // 2
        screen.blit(combined_text, (text_x, self.y * tile_size + 5))

        for obj in objectives:
            if self.x == obj['x'] and self.y == obj['y']:
                pygame.draw.rect(screen, (0, 255, 0), rect, 1)

    def can_move(self, x, y):
        """Vérifie si l'unité peut se déplacer vers une case."""
        if 0 <= x < size and 0 <= y < size:
            if abs(self.x - x) <= 1 and abs(self.y - y) <= 1:
                return True
        return False

    def move(self, x, y):
        """Déplace l'unité vers une case spécifiée."""
        self.x = x
        self.y = y
        self.moved = True

    def attack(self, target_unit, units, objectives):
        """Attaque une unité ennemie."""
        if self.can_move(target_unit.x, target_unit.y):
            dx = target_unit.x - self.x
            dy = target_unit.y - self.y
            new_x, new_y = target_unit.x + dx, target_unit.y + dy

            if target_unit.attacked_this_turn:
                target_unit.pv -= 1
                if target_unit.pv <= 0:
                    units.remove(target_unit)
                    return

            if not (0 <= new_x < size and 0 <= new_y < size) or any(u.x == new_x and u.y == new_y and u.color != target_unit.color for u in units):
                units.remove(target_unit)
            else:
                target_unit.move(new_x, new_y)
                target_unit.attacked_this_turn = True

    def get_symbols_on_same_tile(self, units):
        """Retourne les symboles des unités sur la même case."""
        symbols = [u.get_symbol() for u in units if u.x == self.x and u.y == self.y]
        return ' '.join(symbols)

    def get_symbol(self):
        """Retourne le symbole de l'unité."""
        return "U"

#Classe pour l'ia 
class IA:
    def __init__(self, couleur):
        self.couleur = couleur

    # Fonction qui permet de déplacer l'IA
    def mouvement_ia(self, unite, toutes_les_unites, objectifs):
        """Fait bouger l'unité de l'IA."""
        if not unite.moved:
            # Vérifier si l'unité est sur un objectif majeur ou un objectif mineur            
            sur_objectif_majeur = False # Initialisation du drapeau pour l'objectif majeur
            for obj in objectifs:
                if obj['x'] == unite.x and obj['y'] == unite.y and obj['type'] == 'MAJOR':
                    sur_objectif_majeur = True
                    break  # Sortir de la boucle dès qu'une correspondance est trouvée
            
            sur_objectif_mineur = False # Initialisation du drapeau pour l'objectif mineur
            for obj in objectifs:
                if obj['x'] == unite.x and obj['y'] == unite.y and obj['type'] == 'MINOR':
                    sur_objectif_mineur = True
                    break  # Sortir de la boucle dès qu'une correspondance est trouvée
            
            if (not sur_objectif_majeur) and (not sur_objectif_mineur):
                # Liste des cases adjacentes
                cases_adjacentes = []
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if not (dx == 0 and dy == 0):
                            cases_adjacentes.append((unite.x + dx, unite.y + dy))

                random.shuffle(cases_adjacentes)
                
                for case in cases_adjacentes:
                    x, y = case
                    if (0 <= x < size) and (0 <= y < size) and not any(u.x == x and u.y == y for u in toutes_les_unites):
                        unite.move(x, y)
                        break

    # Fonction qui permet à l'IA d'attaquer
    def attaque_ia(self, unite, toutes_les_unites, objectifs):
        if not unite.attacked_this_turn:
            # Recherche des unités ennemies à portée
            enemies_in_range = [u for u in toutes_les_unites if u.color != unite.color and unite.can_move(u.x, u.y)]
            
            # Attaquer une unité ennemie si possible
            for enemy in enemies_in_range:
                unite.attack(enemy, toutes_les_unites, objectifs)
                return

    # Fonction qui permet d'effectuer le tour de l'IA, si il doit attaquer ou si il doit se déplacer
    def tour_ia(self, toutes_les_unites, objectifs):
        """Contrôle le tour de l'IA."""
        for unite in toutes_les_unites:
            if unite.color == ENEMY_COLOR:
                if not unite.attacked_this_turn:
                    self.attaque_ia(unite, toutes_les_unites, objectifs)
                if (not unite.moved) and (not unite.attacked_this_turn):
                    self.mouvement_ia(unite, toutes_les_unites, objectifs)
                    
# Générer la carte
def generate_map(size):
    """Génère une carte de taille spécifiée."""
    return [[1 for _ in range(size)] for _ in range(size)]

# Afficher la carte
def draw_map(screen, game_map, tile_size):
    """Affiche la carte."""
    for y in range(size):
        for x in range(size):
            color = PASSABLE_COLOR
            pygame.draw.rect(screen, color, (x * tile_size, y * tile_size, tile_size, tile_size))

# Générer des unités sur des cases passables uniquement
def generate_units():
    """Génère les unités pour les joueurs et les ennemis."""
    units = []
    player_positions = [(0, i) for i in range(size)]
    enemy_positions = [(size - 1, i) for i in range(size)]

    player_positions = random.sample(player_positions, 5)
    enemy_positions = random.sample(enemy_positions, 5)

    player_units = [Unit(*pos, PLAYER_COLOR) for pos in player_positions]
    enemy_units = [Unit(*pos, ENEMY_COLOR) for pos in enemy_positions]
    
    units.extend(player_units)
    units.extend(enemy_units)
    
    return units

# Ajouter des objectifs à la carte
def add_objectives():
    """Ajoute des objectifs à la carte."""
    objectives = []
    center_x, center_y = size // 2, size // 2
    while True:
        x, y = random.randint(center_x - 3, center_x + 3), random.randint(center_y - 3, center_y + 3)
        if not any(obj['x'] == x and obj['y'] == y for obj in objectives):
            objectives.append({'x': x, 'y': y, 'type': 'MAJOR'})
            break

    for _ in range(3):
        while True:
            x, y = random.randint(center_x - 5, center_x + 5), random.randint(center_y - 5, center_y + 5)
            if not any(obj['x'] == x and obj['y'] == y for obj in objectives):
                objectives.append({'x': x, 'y': y, 'type': 'MINOR'})
                break

    return objectives

# Afficher les objectifs
def draw_objectives(screen, objectives, tile_size):
    """Affiche les objectifs sur la carte."""
    for obj in objectives:
        color = OBJECTIVE_MAJOR_COLOR if obj['type'] == 'MAJOR' else OBJECTIVE_MINOR_COLOR
        pygame.draw.rect(screen, color, (obj['x'] * tile_size, obj['y'] * tile_size, tile_size, tile_size))

# Calculer les scores
def calculate_scores(units, objectives):
    """Calcule les scores des joueurs et des ennemis en fonction des objectifs contrôlés."""
    player_score = 0
    enemy_score = 0

    for obj in objectives:
        if any(unit.x == obj['x'] and unit.y == obj['y'] and unit.color == PLAYER_COLOR for unit in units):
            player_score += 3 if obj['type'] == 'MAJOR' else 1
        elif any(unit.x == obj['x'] and unit.y == obj['y'] and unit.color == ENEMY_COLOR for unit in units):
            enemy_score += 3 if obj['type'] == 'MAJOR' else 1

    return player_score, enemy_score

# Afficher le message de changement de tour
def draw_turn_indicator(screen, player_turn):
    """Affiche l'indicateur de tour."""
    font = pygame.font.SysFont(None, 36)
    text = "Joueur" if player_turn else "Ennemi"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (260, 10))

# Afficher le bouton de changement de tour
def draw_end_turn_button(screen, width, height, interface_height):
    """Affiche le bouton de fin de tour."""
    font = pygame.font.SysFont(None, 36)
    text = font.render("Terminé", True, (255, 255, 255))
    button_rect = pygame.Rect(width // 2 - 130, height, 270, interface_height)
    pygame.draw.rect(screen, (100, 100, 100), button_rect)
    screen.blit(text, (width // 2 - 40, height + 60))

# Vérifier si le bouton de changement de tour est cliqué
def end_turn_button_clicked(mouse_pos, width, height, interface_height):
    """Vérifie si le bouton de fin de tour a été cliqué."""
    x, y = mouse_pos
    button_rect = pygame.Rect(width // 2 - 50, height, 100, interface_height - 10)
    return button_rect.collidepoint(x, y)

# Afficher les attributs de l'unité sélectionnée
def draw_unit_attributes(screen, unit, width, height, interface_height):
    """Affiche les attributs de l'unité sélectionnée."""
    if unit:
        font = pygame.font.SysFont(None, 24)
        pv_text = f"PV: {unit.pv} / 2"
        unit_img = font.render("Unité", True, (255, 255, 255))
        pv_img = font.render(pv_text, True, (255, 255, 255))
        screen.blit(unit_img, (10, height + 10))
        screen.blit(pv_img, (10, height + 40))

# Afficher les scores
def draw_scores(screen, player_score, enemy_score, width, height):
    """Affiche les scores des joueurs."""
    font = pygame.font.SysFont(None, 24)
    player_score_text = f"Score Joueur: {player_score}"
    enemy_score_text = f"Score Ennemi: {enemy_score}"
    player_score_img = font.render(player_score_text, True, (255, 255, 255))
    enemy_score_img = font.render(enemy_score_text, True, (255, 255, 255))
    screen.blit(player_score_img, (10, height + 70))
    screen.blit(enemy_score_img, (width - 150, height + 70))

# Afficher le message de victoire
def draw_victory_message(screen, message, width, height):
    """Affiche le message de victoire."""
    font = pygame.font.SysFont(None, 48)
    victory_img = font.render(message, True, (255, 255, 255))
    screen.blit(victory_img, (width // 2 - 130, height // 2 + 200))

# Afficher le minuteur pour le temps de réflexion
def dessiner_minuteur(ecran, temps_restant):
    """Affiche le minuteur du temps restant."""
    font = pygame.font.SysFont(None, 30)
    #Affichage selon le temps restant
    if(temps_restant >= 10):   
        texte = font.render(f"Temps jeu: 00:{temps_restant}", True, (0, 0, 0))
    else:
        texte = font.render(f"Temps jeu: 00:0{temps_restant}", True, (0, 0, 0))
    rect = texte.get_rect(topright=(width - 50, 10))
    ecran.blit(texte, rect)
    
def creation_jeu(param_ia):
    # Configuration de la fenêtre
    screen = pygame.display.set_mode((width, height + interface_height))
    pygame.display.set_caption("Carte de 20x20 avec unités et déplacement")

    # Générer une carte de 20 par 20
    game_map = generate_map(size)

    # Générer les unités
    units = generate_units()

    # Ajouter des objectifs
    objectives = add_objectives()

    selected_unit = None
    player_turn = True  # True pour le tour du joueur, False pour le tour de l'ennemi
    units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]
    player_score = 0
    enemy_score = 0
    victory = False
    victory_message = ""

    # Initialisation du temps de jeu (par exemple, 600 secondes = 10 minutes)
    temps_reflexion = 15  # Durée de réflexion en secondes pour chaque joueur
    temps_debut_tour = pygame.time.get_ticks() // 1000
    clock = pygame.time.Clock()

    # Boucle principale du jeu
    running = True
    while running:
        FPS = 30  # Nombre d'images par seconde
        clock.tick(FPS)
        
        temps_actuel = pygame.time.get_ticks() // 1000  # Temps écoulé en secondes
        
        if not victory :
            unit_moved = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if end_turn_button_clicked((x, y), width, height, interface_height):
                        unit_moved = True
                    else:
                        grid_x, grid_y = x // tile_size, y // tile_size
                        if event.button == 1:  # Clic gauche pour sélectionner
                            possible_units = [u for u in units if u.x == grid_x and u.y == grid_y and not u.moved and u.color == (PLAYER_COLOR if player_turn else ENEMY_COLOR)]
                            if selected_unit in possible_units:
                                current_index = possible_units.index(selected_unit)
                                selected_unit.selected = False
                                selected_unit = possible_units[(current_index + 1) % len(possible_units)]
                            else:
                                if selected_unit:
                                    selected_unit.selected = False
                                if possible_units:
                                    selected_unit = possible_units[0]
                            if selected_unit:
                                selected_unit.selected = True
                        elif event.button == 3:  # Clic droit pour déplacer ou attaquer
                            if selected_unit and selected_unit.color == (PLAYER_COLOR if player_turn else ENEMY_COLOR):
                                target_unit = [u for u in units if u.x == grid_x and u.y == grid_y and u.color != selected_unit.color]
                                
                                for cible in target_unit:                                
                                    selected_unit.attack(cible, units, objectives)
                                    
                                if selected_unit.can_move(grid_x, grid_y):
                                    selected_unit.move(grid_x, grid_y)
                                    selected_unit.selected = False
                                    selected_unit = None

            # Calcul du temps écoulé depuis le début du tour
            temps_actuel = pygame.time.get_ticks() // 1000
            temps_ecoule = temps_actuel - temps_debut_tour
            
            if unit_moved or temps_ecoule >= temps_reflexion:
                for unit in units_to_move:
                    unit.moved = False  # Réinitialiser l'indicateur de mouvement
                    unit.attacked_this_turn = False  # Réinitialiser l'indicateur d'attaque
                player_turn = not player_turn
                units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]
                player_score_turn, enemy_score_turn = calculate_scores(units, objectives)
                player_score += player_score_turn
                enemy_score += enemy_score_turn

                if player_score >= 500:
                    victory = True
                    victory_message = "Victoire Joueur!"
                elif enemy_score >= 500:
                    victory = True
                    victory_message = "Victoire Ennemi!"
                elif not any(unit.color == PLAYER_COLOR for unit in units):
                    victory = True
                    victory_message = "Victoire Ennemi!"
                elif not any(unit.color == ENEMY_COLOR for unit in units):
                    victory = True
                    victory_message = "Victoire Joueur!"
                
                if param_ia:
                    robot = IA(ENEMY_COLOR_LIGHT)
                    if not player_turn:
                        robot.tour_ia(units, objectives)
                        player_turn = True
                        for unit in units:
                            unit.moved = False
                            unit.attacked_this_turn = False

                temps_debut_tour = pygame.time.get_ticks() // 1000
                pygame.display.flip()

        screen.fill((0, 0, 0))
        draw_map(screen, game_map, tile_size)
        draw_objectives(screen, objectives, tile_size)
        
        for unit in units:
            unit.draw(screen, units, objectives)

        draw_turn_indicator(screen, player_turn)
        draw_end_turn_button(screen, width, height, interface_height)
        draw_unit_attributes(screen, selected_unit, width, height, interface_height)
        draw_scores(screen, player_score, enemy_score, width, height)
        dessiner_minuteur(screen, temps_reflexion - temps_ecoule)

        if victory:
            img = pygame.image.load("jeuPython/victory.jpg")
            img = pygame.transform.scale(img, (width, height))
            screen.blit(img, (0, 0))
            draw_victory_message(screen, victory_message, width, height)
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

        pygame.display.flip()

    pygame.quit()


#Lancement de la fênetre Menu
screen = pygame.display.set_mode((250, 100 + 50))
pygame.display.set_caption("Menu Principal")
font = pygame.font.SysFont("Times New Roman", 32)
menu_options = ["PVP", "IA"]
running = True

while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            for i, option in enumerate(menu_options):
                text = font.render(option, True, (255, 255, 255))
                rect = text.get_rect(center=(125, 50  + i * 60))
                if rect.collidepoint(x, y):
                    if i == 0:
                        creation_jeu(False) #Lancement du jeu dans le cas d'un Joueur contre Joueur
                    elif i == 1:
                        creation_jeu(True) #Lancement du jeu dans le cas d'un Joueur contre IA
                    running = False

    for i, option in enumerate(menu_options):
        color = (238,130,238) if i == 0 else (255, 255, 255)
        text = font.render(option, True, color)
        rect = text.get_rect(center=(125, 50  + i * 60))
        pygame.draw.rect(screen, (238,130,238) if i == 1 else (255, 255, 255), rect.inflate(20, 20), 3)
        screen.blit(text, rect.topleft)

    pygame.display.flip()

pygame.quit()
